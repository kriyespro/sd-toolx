"""Template context processors."""
from django.conf import settings


def site_context(request):
    profile = None
    if request.user.is_authenticated:
        profile = getattr(request.user, "profile", None)

    return {
        "site_name": "SD-Toolx",
        "site_tagline": "44 Free Tools. No Signup. No Ads.",
        "profile": profile,
        "free_ops_per_day": settings.FREE_OPS_PER_DAY,
    }
