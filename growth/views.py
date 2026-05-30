from django.contrib.auth import get_user_model, login
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from billing.services.subscription_service import start_trial
from features.tools.models import ToolJob
from users.models import Profile, ReferralLog

User = get_user_model()


def join_referral(request, code):
    profile = get_object_or_404(Profile, referral_code=code.upper())
    request.session["referral_code"] = profile.referral_code
    return redirect("users:register")


@require_POST
def email_capture(request):
    email = request.POST.get("email", "").strip().lower()
    if not email or "@" not in email:
        return render(
            request,
            "partials/_email_capture_error.jinja",
            {"message": "Enter a valid email."},
            status=200,
        )

    user, created = User.objects.get_or_create(email=email, defaults={"is_active": True})
    if created:
        user.set_unusable_password()
        user.save()
        start_trial(user)
        ref_code = request.session.pop("referral_code", None)
        if ref_code:
            try:
                referrer = Profile.objects.get(referral_code=ref_code)
                user.profile.referred_by = referrer
                user.profile.save(update_fields=["referred_by"])
                ReferralLog.objects.create(
                    referrer=referrer,
                    referee=user,
                    referee_email=email,
                )
            except Profile.DoesNotExist:
                pass

    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return render(request, "partials/_trial_activated.jinja", {"email": email})


def stats_partial(request):
    total = cache.get("tool_stats_total")
    if total is None:
        total = ToolJob.objects.filter(status=ToolJob.STATUS_DONE).count()
        cache.set("tool_stats_total", total, 60)
    users = cache.get("tool_stats_users")
    if users is None:
        users = Profile.objects.count() + 1200
        cache.set("tool_stats_users", users, 60)
    return render(
        request,
        "partials/_social_proof.jinja",
        {"files_processed": total, "user_count": users},
    )


def launch_page(request):
    return render(request, "pages/launch.jinja")


def short_link_redirect(request, code):
    from growth.models import ShortLink
    link = get_object_or_404(ShortLink, code=code)
    link.click_count += 1
    link.save(update_fields=["click_count"])
    return redirect(link.target_url)


@require_http_methods(["GET", "POST"])
def student_page(request):
    message = ""
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        if email.endswith(".edu") or email.endswith(".ac.in"):
            message = "Student discount approved! Use code STUDENT50 at checkout (coming soon)."
        else:
            message = "Use your college .edu or .ac.in email for 50% off Pro."
    return render(request, "pages/student.jinja", {"message": message})

