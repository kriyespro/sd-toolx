"""Custom user and profile models."""
import secrets
import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from users.managers import UserManager


def generate_referral_code():
    return secrets.token_hex(3).upper()[:6]


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    plan = models.ForeignKey(
        "billing.Plan",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profiles",
    )
    api_key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    referral_code = models.CharField(max_length=6, unique=True, default=generate_referral_code)
    referred_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referrals",
    )
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    ops_today = models.PositiveIntegerField(default=0)
    ops_reset_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "profiles"

    def __str__(self):
        return f"Profile({self.user.email})"

    @property
    def is_on_trial(self):
        if not self.trial_ends_at:
            return False
        return timezone.now() < self.trial_ends_at


class ReferralLog(models.Model):
    referrer = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="referrals_sent"
    )
    referee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referral_signups",
    )
    referee_email = models.EmailField(blank=True)
    reward_given = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.referrer.referral_code} → {self.referee_email or self.referee_id}"
