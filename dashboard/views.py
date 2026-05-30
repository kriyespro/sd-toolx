import uuid

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from features.tools.models import ToolJob
from features.tools.services.limits import get_limits, get_ops_used


@login_required
def home(request):
    profile = request.user.profile
    profile.reset_ops_if_needed()
    limits = get_limits(request)
    recent_jobs = ToolJob.objects.filter(user=request.user)[:10]

    ops_limit = "Unlimited" if limits.is_unlimited_ops or limits.ops_per_day < 0 else limits.ops_per_day
    ops_used = get_ops_used(request)
    usage_pct = 0
    if ops_limit != "Unlimited" and isinstance(ops_limit, int) and ops_limit > 0:
        usage_pct = min(100, int(ops_used / ops_limit * 100))

    subscription = None
    if hasattr(request.user, "subscription"):
        try:
            subscription = request.user.subscription
        except Exception:
            subscription = None

    return render(
        request,
        "pages/dashboard.jinja",
        {
            "profile": profile,
            "recent_jobs": recent_jobs,
            "ops_used": ops_used,
            "ops_limit": ops_limit,
            "usage_pct": usage_pct,
            "subscription": subscription,
        },
    )


@login_required
def api_key_page(request):
    profile = request.user.profile
    has_api = bool(profile.plan and profile.plan.has_api)
    return render(request, "pages/api_key.jinja", {
        "profile": profile,
        "has_api": has_api,
        "api_key": str(profile.api_key) if has_api else None,
    })


@login_required
@require_POST
def regenerate_api_key(request):
    profile = request.user.profile
    if not (profile.plan and profile.plan.has_api):
        return JsonResponse({"error": "API access requires Business plan."}, status=403)
    profile.api_key = uuid.uuid4()
    profile.save(update_fields=["api_key"])
    return redirect("dashboard:api-key")
