"""Razorpay integration."""
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def is_configured() -> bool:
    return bool(settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET)


def get_client():
    if not is_configured():
        return None
    import razorpay

    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def create_order(user, plan, is_annual: bool) -> dict:
    """Create Razorpay order for plan purchase."""
    amount = plan.price_yearly_paise if is_annual else plan.price_monthly_paise
    receipt = f"{plan.slug}_{user.id}_{'y' if is_annual else 'm'}"

    if not is_configured():
        return {
            "dev_mode": True,
            "amount": amount,
            "currency": "INR",
            "receipt": receipt,
            "plan_slug": plan.slug,
            "is_annual": is_annual,
        }

    client = get_client()
    order = client.order.create(
        {
            "amount": amount,
            "currency": "INR",
            "receipt": receipt[:40],
            "notes": {
                "user_id": str(user.id),
                "plan_slug": plan.slug,
                "is_annual": str(is_annual),
            },
        }
    )
    return {
        "id": order["id"],
        "amount": order["amount"],
        "currency": order["currency"],
        "key_id": settings.RAZORPAY_KEY_ID,
    }


def verify_payment(order_id: str, payment_id: str, signature: str) -> bool:
    if not is_configured():
        return True
    client = get_client()
    try:
        client.utility.verify_payment_signature(
            {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }
        )
        return True
    except Exception as exc:
        logger.warning("Payment verification failed: %s", exc)
        return False


def verify_webhook_signature(body: bytes, signature: str) -> bool:
    if not is_configured() or not settings.RAZORPAY_WEBHOOK_SECRET:
        return settings.DEBUG
    import razorpay

    try:
        razorpay.Utility.verify_webhook_signature(
            body.decode("utf-8"),
            signature,
            settings.RAZORPAY_WEBHOOK_SECRET,
        )
        return True
    except Exception as exc:
        logger.warning("Webhook verification failed: %s", exc)
        return False
