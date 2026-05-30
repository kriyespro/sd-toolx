import json
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST

from billing.models import Plan
from billing.services import razorpay_service
from billing.services.subscription_service import activate_plan, cancel_subscription

logger = logging.getLogger(__name__)


def pricing(request):
    plans = Plan.objects.filter(is_active=True).exclude(slug="free")
    free = Plan.objects.filter(slug="free").first()
    return render(
        request,
        "pages/pricing.jinja",
        {
            "plans": plans,
            "free_plan": free,
            "razorpay_configured": razorpay_service.is_configured(),
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        },
    )


@login_required
@require_POST
def create_checkout(request):
    """Create Razorpay order (JSON for frontend)."""
    plan_slug = request.POST.get("plan_slug")
    is_annual = request.POST.get("is_annual") == "true"
    plan = get_object_or_404(Plan, slug=plan_slug, is_active=True)

    if plan.slug == "free":
        return JsonResponse({"error": "Cannot purchase free plan"}, status=400)

    order = razorpay_service.create_order(request.user, plan, is_annual)

    if order.get("dev_mode") and settings.DEBUG:
        request.session["pending_checkout"] = {
            "plan_slug": plan.slug,
            "is_annual": is_annual,
        }
        return JsonResponse(
            {
                "dev_mode": True,
                "confirm_url": "/billing/dev-confirm/",
                "plan_name": plan.name,
                "amount": order["amount"],
            }
        )

    return JsonResponse(order)


@login_required
def dev_confirm(request):
    """DEV ONLY: activate plan without Razorpay when keys not configured."""
    if not settings.DEBUG or razorpay_service.is_configured():
        return HttpResponseBadRequest("Not available")

    pending = request.session.pop("pending_checkout", None)
    if not pending:
        return redirect("billing:pricing")

    plan = get_object_or_404(Plan, slug=pending["plan_slug"])
    activate_plan(
        request.user,
        plan,
        is_annual=pending["is_annual"],
        payment_id=f"dev_{request.user.id}_{plan.slug}",
    )
    return redirect("dashboard:home")


@login_required
@require_POST
def confirm_payment(request):
    """Verify Razorpay payment and activate plan."""
    order_id = request.POST.get("razorpay_order_id", "")
    payment_id = request.POST.get("razorpay_payment_id", "")
    signature = request.POST.get("razorpay_signature", "")
    plan_slug = request.POST.get("plan_slug", "")
    is_annual = request.POST.get("is_annual") == "true"

    plan = get_object_or_404(Plan, slug=plan_slug)

    if not razorpay_service.verify_payment(order_id, payment_id, signature):
        return JsonResponse({"error": "Payment verification failed"}, status=400)

    amount = plan.price_yearly_paise if is_annual else plan.price_monthly_paise
    activate_plan(
        request.user,
        plan,
        is_annual=is_annual,
        payment_id=payment_id,
        amount_paise=amount,
    )
    return JsonResponse({"success": True, "redirect": "/dashboard/"})


@login_required
@require_POST
def cancel_plan(request):
    cancel_subscription(request.user)
    return redirect("dashboard:home")


@csrf_exempt
@require_POST
def razorpay_webhook(request):
    signature = request.META.get("HTTP_X_RAZORPAY_SIGNATURE", "")
    body = request.body

    if not razorpay_service.verify_webhook_signature(body, signature):
        return HttpResponseBadRequest("Invalid signature")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    event = payload.get("event", "")
    entity = payload.get("payload", {}).get("payment", {}).get("entity", {})

    if event == "payment.captured":
        notes = entity.get("notes", {})
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user_id = notes.get("user_id")
        plan_slug = notes.get("plan_slug")
        if user_id and plan_slug:
            try:
                user = User.objects.get(pk=user_id)
                plan = Plan.objects.get(slug=plan_slug)
                is_annual = notes.get("is_annual") == "True"
                activate_plan(
                    user,
                    plan,
                    is_annual=is_annual,
                    payment_id=entity.get("id", ""),
                    amount_paise=entity.get("amount", 0),
                )
            except (User.DoesNotExist, Plan.DoesNotExist):
                logger.exception("Webhook user/plan not found")

    elif event == "subscription.cancelled":
        from django.contrib.auth import get_user_model

        User = get_user_model()
        notes = payload.get("payload", {}).get("subscription", {}).get("entity", {}).get(
            "notes", {}
        )
        user_id = notes.get("user_id")
        if user_id:
            try:
                cancel_subscription(User.objects.get(pk=user_id))
            except User.DoesNotExist:
                pass

    return HttpResponse("OK")
