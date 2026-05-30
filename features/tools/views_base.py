"""Base tool views and HTMX job endpoints."""
from django.db import transaction
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views import View

from features.tools.models import ToolJob
from features.tools.registry import get_tool
from features.tools.seo_data import build_json_ld, get_seo
from features.tools.services import file_handler
from features.tools.services.exceptions import FileValidationError, ToolError, UpgradeRequired
from features.tools.services.limits import check_can_process, increment_usage
from features.tools.tasks import process_tool


def _ensure_session(request):
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key


def _create_job(request, tool_slug, options=None):
    session_key = _ensure_session(request)
    job = ToolJob.objects.create(
        user=request.user if request.user.is_authenticated else None,
        session_key=session_key,
        tool_slug=tool_slug,
        options=options or {},
        status=ToolJob.STATUS_PENDING,
    )
    job.mark_expired()
    job.save(update_fields=["expires_at"])
    return job


class ToolPageView(View):
    """GET: tool page. POST: process upload."""

    tool_slug = None

    def get_tool_meta(self):
        return get_tool(self.tool_slug)

    def get(self, request):
        tool = self.get_tool_meta()
        seo = {**tool.get("seo", {}), **get_seo(self.tool_slug)}
        return render(
            request,
            tool["template"],
            {
                "tool": tool,
                "seo": seo,
                "seo_json_ld": build_json_ld(tool, seo, request),
            },
        )

    def get_allowed_extensions(self, tool):
        return set(tool.get("extensions", []))

    def get_uploads(self, request, tool):
        if tool.get("no_upload"):
            return []
        if tool.get("multiple"):
            return request.FILES.getlist("files")
        f = request.FILES.get("file")
        return [f] if f else []

    def build_options(self, request, tool):
        opts = {}
        for key in tool.get("option_fields", []):
            if key in request.POST:
                opts[key] = request.POST.get(key)
        return opts

    def post(self, request):
        tool = self.get_tool_meta()
        uploads = self.get_uploads(request, tool)

        if not tool.get("no_upload") and not uploads:
            return self._error_response(request, tool, "Please select a file.")

        try:
            file_count = len(uploads) if uploads else 1
            limits = check_can_process(request, file_count=file_count)
            allowed = self.get_allowed_extensions(tool)

            job = _create_job(request, self.tool_slug, self.build_options(request, tool))

            if uploads:
                paths = []
                for i, upload in enumerate(uploads):
                    file_handler.validate_file(upload, limits.max_file_mb, allowed)
                    paths.append(file_handler.save_upload(job, upload, i))
                job.input_files = paths

            if tool.get("no_upload"):
                job.options = {**job.options, **self.build_options(request, tool)}
                job.save(update_fields=["options"])

            job.save(update_fields=["input_files", "options"])

            with transaction.atomic():
                increment_usage(request)

            from features.tools.job_runner import dispatch_tool_job

            job.status = ToolJob.STATUS_PROCESSING
            job.compression_stat = {"progress": 3, "stage": "Starting…"}
            job.save(update_fields=["status", "compression_stat"])
            dispatch_tool_job(job.id)
            job.refresh_from_db()

            context = {"job": job, "tool": tool}
            if not request.user.is_authenticated:
                ops = request.session.get("anon_tool_ops", 0) + 1
                request.session["anon_tool_ops"] = ops
                if ops >= 2:
                    context["show_email_capture"] = True

            return _render_partial(
                request,
                "partials/_job_status.jinja",
                context,
            )

        except UpgradeRequired as exc:
            return _render_partial(
                request,
                "partials/_upgrade_prompt.jinja",
                {"message": exc.message},
            )
        except (FileValidationError, ToolError) as exc:
            return self._error_response(request, tool, exc.message)

    def _error_response(self, request, tool, message):
        return _render_partial(
            request,
            "partials/_tool_error.jinja",
            {"tool": tool, "message": message},
        )


def _render_partial(request, template, context):
    """HTMX swaps only on 2xx — always return 200 for partials."""
    return render(request, template, context, status=200)


def job_status(request, job_id):
    job = get_object_or_404(ToolJob, pk=job_id)
    tool = get_tool(job.tool_slug)
    if job.status == ToolJob.STATUS_DONE and job.output_file and not job.output_url:
        job.output_url = file_handler.download_url(request, job.output_file)
        job.save(update_fields=["output_url"])
    return _render_partial(
        request,
        "partials/_job_status.jinja",
        {"job": job, "tool": tool},
    )


def job_download(request, job_id):
    job = get_object_or_404(ToolJob, pk=job_id)
    if job.status != ToolJob.STATUS_DONE or not job.output_file:
        return HttpResponseForbidden("Not ready")
    from django.http import FileResponse

    path = file_handler.to_absolute(job.output_file)
    download_name = path.name
    if job.tool_slug == "compress-pdf":
        download_name = "compressed.pdf"
    elif job.tool_slug == "merge-pdf":
        download_name = "merged-compressed.pdf"
    elif job.tool_slug == "ai-summarize-pdf":
        download_name = "summary.txt"
    elif job.tool_slug == "remove-background":
        download_name = "no-background.png"
    elif job.tool_slug == "compress-image":
        from pathlib import Path

        download_name = Path(job.output_file).name if job.output_file else "compressed.jpg"
    response = FileResponse(open(path, "rb"), as_attachment=True, filename=download_name)
    return response


def recent_files_partial(request):
    session_key = _ensure_session(request)
    since = timezone.now() - timezone.timedelta(hours=24)
    jobs = ToolJob.objects.filter(
        session_key=session_key,
        status=ToolJob.STATUS_DONE,
        created_at__gte=since,
    )[:5]
    return render(request, "partials/_recent_files.jinja", {"jobs": jobs})
