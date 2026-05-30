"""Billing and subscription models."""
from django.conf import settings
from django.db import models


class Plan(models.Model):
    name = models.CharField(max_length=64)
    slug = models.SlugField(unique=True)
    price_monthly_paise = models.PositiveIntegerField(help_text="INR paise")
    price_yearly_paise = models.PositiveIntegerField(help_text="INR paise")
    ops_per_day = models.IntegerField(
        help_text="-1 = unlimited"
    )
    max_file_mb = models.PositiveIntegerField()
    max_files = models.IntegerField(help_text="-1 = unlimited")
    has_batch = models.BooleanField(default=False)
    has_ai = models.BooleanField(default=False)
    has_api = models.BooleanField(default=False)
    has_esign_unlimited = models.BooleanField(default=False)
    has_team = models.BooleanField(default=False)
    team_seats = models.PositiveIntegerField(default=1)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.name

    @property
    def price_monthly_inr(self):
        return self.price_monthly_paise / 100

    @property
    def price_yearly_inr(self):
        return self.price_yearly_paise / 100


class Subscription(models.Model):
    STATUS_CHOICES = [
        ("trialing", "Trialing"),
        ("active", "Active"),
        ("past_due", "Past due"),
        ("cancelled", "Cancelled"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscription",
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    razorpay_subscription_id = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="trialing")
    is_annual = models.BooleanField(default=False)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} — {self.plan.slug}"


class Invoice(models.Model):
    subscription = models.ForeignKey(
        Subscription, on_delete=models.CASCADE, related_name="invoices"
    )
    razorpay_payment_id = models.CharField(max_length=128, unique=True)
    amount_paise = models.PositiveIntegerField()
    paid_at = models.DateTimeField()
    receipt_url = models.URLField(blank=True)

    def __str__(self):
        return f"Invoice {self.razorpay_payment_id}"
