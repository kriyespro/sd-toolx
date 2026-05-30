from django.contrib import admin

from billing.models import Invoice, Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "price_monthly_inr",
        "ops_per_day",
        "max_file_mb",
        "is_active",
    )
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "status", "is_annual", "current_period_end")
    list_filter = ("status", "plan")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("razorpay_payment_id", "subscription", "amount_paise", "paid_at")
