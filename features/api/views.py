"""REST API — v1 endpoints for B2B tool access."""
import json
import uuid
from pathlib import Path

from django.http import JsonResponse, FileResponse, HttpResponseBadRequest
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from features.tools.models import ToolJob
from features.tools.registry import get_tool, TOOLS
from features.tools.services import file_handler
from features.tools.tasks import process_tool
from users.models import Profile


def _authenticate(request) -> Profile | None:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        key = auth[7:].strip()
    elif auth.startswith("Api-Key "):
        key = auth[8:].strip()
    else:
        key = request.GET.get("api_key", "")
    if not key:
        return None
    try:
        uid = uuid.UUID(key)
        return Profile.objects.select_related("user", "plan").get(api_key=uid)
    except (ValueError, Profile.DoesNotExist):
        return None


def _error(msg: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"error": msg}, status=status)


def _job_to_dict(job: ToolJob, request) -> dict:
    data = {
        "id": job.pk,
        "tool": job.tool_slug,
        "status": job.status,
        "created_at": job.created_at.isoformat(),
        "expires_at": job.expires_at.isoformat() if job.expires_at else None,
    }
    if job.status == ToolJob.STATUS_DONE:
        data["download_url"] = request.build_absolute_uri(f"/api/v1/jobs/{job.pk}/download/")
        if job.compression_stat:
            data["stats"] = job.compression_stat
    elif job.status == ToolJob.STATUS_FAILED:
        data["error"] = job.error_message or "Processing failed."
    elif job.status == ToolJob.STATUS_PROCESSING:
        stat = job.compression_stat or {}
        data["progress"] = stat.get("progress", 0)
        data["stage"] = stat.get("stage", "Processing…")
    return data


@method_decorator(csrf_exempt, name="dispatch")
class JobSubmitView(View):
    """POST /api/v1/jobs/ — submit a new tool job."""

    def post(self, request):
        profile = _authenticate(request)
        if not profile:
            return _error("Invalid or missing API key.", 401)

        if not (profile.plan and profile.plan.has_api):
            return _error("API access requires a Business plan.", 403)

        try:
            body = json.loads(request.body) if request.content_type == "application/json" else {}
        except json.JSONDecodeError:
            body = {}

        tool_slug = body.get("tool") or request.POST.get("tool", "")
        if not tool_slug:
            return _error("'tool' field required.")

        try:
            tool_meta = get_tool(tool_slug)
        except KeyError:
            return _error(f"Unknown tool '{tool_slug}'.")

        opts = body.get("options", {}) or {}

        job = ToolJob.objects.create(
            user=profile.user,
            tool_slug=tool_slug,
            status=ToolJob.STATUS_PENDING,
            options=opts,
            input_files=[],
            expires_at=timezone.now() + timezone.timedelta(hours=2),
        )

        files = request.FILES.getlist("files")
        input_rels = []
        for i, f in enumerate(files):
            rel = file_handler.save_upload(job, f, index=i)
            input_rels.append(rel)
        job.input_files = input_rels
        job.save(update_fields=["input_files"])

        process_tool.apply_async(args=[job.pk], queue="default")

        return JsonResponse(_job_to_dict(job, request), status=202)


@method_decorator(csrf_exempt, name="dispatch")
class JobStatusView(View):
    """GET /api/v1/jobs/<id>/ — poll job status."""

    def get(self, request, job_id: int):
        profile = _authenticate(request)
        if not profile:
            return _error("Invalid or missing API key.", 401)

        try:
            job = ToolJob.objects.get(pk=job_id, user=profile.user)
        except ToolJob.DoesNotExist:
            return _error("Job not found.", 404)

        return JsonResponse(_job_to_dict(job, request))


@method_decorator(csrf_exempt, name="dispatch")
class JobDownloadView(View):
    """GET /api/v1/jobs/<id>/download/ — download result file."""

    def get(self, request, job_id: int):
        profile = _authenticate(request)
        if not profile:
            return _error("Invalid or missing API key.", 401)

        try:
            job = ToolJob.objects.get(pk=job_id, user=profile.user)
        except ToolJob.DoesNotExist:
            return _error("Job not found.", 404)

        if job.status != ToolJob.STATUS_DONE:
            return _error(f"Job not ready (status: {job.status}).", 409)

        if not job.output_file:
            return _error("No output file.", 500)

        path = file_handler.to_absolute(job.output_file)
        if not path.exists():
            return _error("Output file expired or missing.", 410)

        return FileResponse(open(path, "rb"), filename=path.name, as_attachment=True)


@method_decorator(csrf_exempt, name="dispatch")
class ToolListView(View):
    """GET /api/v1/tools/ — list available tools."""

    def get(self, request):
        profile = _authenticate(request)
        if not profile:
            return _error("Invalid or missing API key.", 401)

        tools = [
            {
                "slug": t["slug"],
                "name": t["name"],
                "category": t["category"],
                "description": t["description"],
                "multiple_files": t.get("multiple", False),
                "accepted_extensions": sorted(t.get("extensions", set())),
            }
            for t in TOOLS if t.get("is_live")
        ]
        return JsonResponse({"tools": tools, "count": len(tools)})


@method_decorator(csrf_exempt, name="dispatch")
class ApiKeyInfoView(View):
    """GET /api/v1/me/ — return API key info."""

    def get(self, request):
        profile = _authenticate(request)
        if not profile:
            return _error("Invalid or missing API key.", 401)

        return JsonResponse({
            "email": profile.user.email,
            "plan": profile.plan.slug if profile.plan else "free",
            "api_access": bool(profile.plan and profile.plan.has_api),
            "api_key": str(profile.api_key),
        })
