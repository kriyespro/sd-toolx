"""Activate and manage user subscriptions."""
from datetime import timedelta

from django.utils import timezone

from billing.models import Invoice, Plan, Subscription
from billing.services import emails


def get_free_plan():
    return Plan.objects.filter(slug="free").first()


def activate_plan(user, plan, is_annual: bool = False, payment_id: str = "", amount_paise: int = 0):
    """Apply plan to user after successful payment."""
    profile = user.profile
    profile.plan = plan
    profile.trial_ends_at = None
    profile.save(update_fields=["plan", "trial_ends_at"])

    period_days = 365 if is_annual else 30
    period_end = timezone.now() + timedelta(days=period_days)

    sub, _ = Subscription.objects.update_or_create(
        user=user,
        defaults={
            "plan": plan,
            "status": "active",
            "is_annual": is_annual,
            "current_period_end": period_end,
            "cancelled_at": None,
        },
    )

    if payment_id:
        Invoice.objects.get_or_create(
            razorpay_payment_id=payment_id,
            defaults={
                "subscription": sub,
                "amount_paise": amount_paise or (
                    plan.price_yearly_paise if is_annual else plan.price_monthly_paise
                ),
                "paid_at": timezone.now(),
            },
        )
        emails.send_payment_success(user, plan)

    return sub


def cancel_subscription(user):
    """Downgrade user to free plan."""
    free = get_free_plan()
    profile = user.profile
    if free:
        profile.plan = free
    profile.save(update_fields=["plan"])

    try:
        sub = user.subscription
        sub.status = "cancelled"
        sub.cancelled_at = timezone.now()
        sub.save(update_fields=["status", "cancelled_at"])
    except Subscription.DoesNotExist:
        pass

    emails.send_cancellation(user)


def start_trial(user, days: int = 7):
    """Start Pro trial for new users."""
    pro = Plan.objects.filter(slug="pro").first()
    if not pro:
        return
    profile = user.profile
    profile.trial_ends_at = timezone.now() + timedelta(days=days)
    if not profile.plan_id:
        profile.plan = get_free_plan() or pro
    profile.save(update_fields=["trial_ends_at", "plan"])
    emails.send_trial_start(user)
