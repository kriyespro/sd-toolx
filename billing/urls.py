from django.urls import path

from billing import views

app_name = "billing"

urlpatterns = [
    path("pricing/", views.pricing, name="pricing"),
    path("checkout/create/", views.create_checkout, name="checkout-create"),
    path("checkout/confirm/", views.confirm_payment, name="checkout-confirm"),
    path("dev-confirm/", views.dev_confirm, name="dev-confirm"),
    path("cancel/", views.cancel_plan, name="cancel"),
    path("webhook/razorpay/", views.razorpay_webhook, name="webhook"),
]
