"""Freemium limit checks and usage tracking."""
from dataclasses import dataclass

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from billing.models import Plan
from features.tools.services.exceptions import UpgradeRequired


@dataclass
class ToolLimits:
    ops_per_day: int
    max_file_mb: int
    max_files: int
    is_unlimited_ops: bool = False


def _free_plan():
    return Plan.objects.filter(slug="free").first()


def get_limits(request) -> ToolLimits:
    if request.user.is_authenticated:
        profile = request.user.profile
        profile.reset_ops_if_needed()
        if profile.is_on_trial:
            pro = Plan.objects.filter(slug="pro").first()
            if pro:
                return ToolLimits(
                    ops_per_day=pro.ops_per_day,
                    max_file_mb=pro.max_file_mb,
                    max_files=pro.max_files,
                    is_unlimited_ops=pro.ops_per_day < 0,
                )
        if profile.plan_id:
            plan = profile.plan
            return ToolLimits(
                ops_per_day=plan.ops_per_day,
                max_file_mb=plan.max_file_mb,
                max_files=plan.max_files,
                is_unlimited_ops=plan.ops_per_day < 0,
            )
    free = _free_plan()
    if free:
        return ToolLimits(
            ops_per_day=free.ops_per_day,
            max_file_mb=free.max_file_mb,
            max_files=free.max_files,
        )
    return ToolLimits(
        ops_per_day=settings.FREE_OPS_PER_DAY,
        max_file_mb=settings.FREE_MAX_FILE_MB,
        max_files=settings.FREE_MAX_FILES,
    )


def _session_cache_key(session_key: str) -> str:
    return f"tool_ops:{session_key}:{timezone.localdate()}"


def get_ops_used(request) -> int:
    if request.user.is_authenticated:
        profile = request.user.profile
        profile.reset_ops_if_needed()
        return profile.ops_today
    if not request.session.session_key:
        request.session.save()
    return cache.get(_session_cache_key(request.session.session_key), 0)


def check_can_process(request, file_count: int = 1) -> ToolLimits:
    limits = get_limits(request)
    used = get_ops_used(request)

    if not limits.is_unlimited_ops and limits.ops_per_day >= 0 and used >= limits.ops_per_day:
        raise UpgradeRequired(
            f"You've used your {limits.ops_per_day} free operations today. "
            "Upgrade to Pro for unlimited access."
        )

    max_files = limits.max_files if limits.max_files > 0 else 999
    if file_count > max_files:
        raise UpgradeRequired(
            f"Your plan allows up to {max_files} files per operation. Upgrade for more."
        )

    return limits


def increment_usage(request):
    if request.user.is_authenticated:
        profile = request.user.profile
        profile.reset_ops_if_needed()
        profile.ops_today += 1
        profile.save(update_fields=["ops_today", "ops_reset_date"])

        from features.tools.models import UsageLog

        log, _ = UsageLog.objects.get_or_create(
            user=request.user,
            date=timezone.localdate(),
            defaults={"op_count": 0},
        )
        log.op_count += 1
        log.save(update_fields=["op_count"])
    else:
        if not request.session.session_key:
            request.session.save()
        key = _session_cache_key(request.session.session_key)
        cache.set(key, cache.get(key, 0) + 1, timeout=86400)
