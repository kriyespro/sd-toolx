"""Billing-related emails (console in dev)."""
from django.conf import settings
from django.core.mail import send_mail


def _send(user, subject: str, message: str):
    if not user.email:
        return
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True,
    )


def send_payment_success(user, plan):
    _send(
        user,
        f"Payment confirmed — {plan.name} plan active",
        f"Hi,\n\nYour {plan.name} plan is now active on SD-Toolx.\n\nThank you!",
    )


def send_payment_failed(user):
    _send(
        user,
        "Payment failed — SD-Toolx",
        "Hi,\n\nYour payment could not be processed. Please try again at /billing/pricing/",
    )


def send_trial_start(user):
    _send(
        user,
        "Your 7-day Pro trial started — SD-Toolx",
        "Hi,\n\nYou have 7 days of Pro access free. No credit card required.\n\nEnjoy!",
    )


def send_trial_ending(user):
    _send(
        user,
        "Trial ends in 2 days — SD-Toolx",
        "Hi,\n\nYour Pro trial ends soon. Upgrade at /billing/pricing/ to keep unlimited access.",
    )


def send_cancellation(user):
    _send(
        user,
        "Subscription cancelled — SD-Toolx",
        "Hi,\n\nYour subscription was cancelled. You are on the free plan.\n\nCome back anytime!",
    )
