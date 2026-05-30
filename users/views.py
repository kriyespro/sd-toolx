from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from users.forms import SignupForm


@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        from billing.services.subscription_service import start_trial
        from users.models import Profile, ReferralLog

        start_trial(user)
        ref_code = request.session.pop("referral_code", None)
        if ref_code:
            try:
                referrer = Profile.objects.get(referral_code=ref_code)
                user.profile.referred_by = referrer
                user.profile.save(update_fields=["referred_by"])
                ReferralLog.objects.create(
                    referrer=referrer, referee=user, referee_email=user.email
                )
            except Profile.DoesNotExist:
                pass
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect("dashboard:home")
    return render(request, "pages/auth/register.jinja", {"form": form})


@login_required
def profile_settings(request):
    return render(request, "pages/auth/profile.jinja")
