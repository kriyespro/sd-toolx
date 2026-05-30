from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import Profile, ReferralLog, User


class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 0
    readonly_fields = ("api_key", "referral_code")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("email",)
    list_display = ("email", "is_staff", "is_active", "date_joined")
    search_fields = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )
    inlines = [ProfileInline]


@admin.register(ReferralLog)
class ReferralLogAdmin(admin.ModelAdmin):
    list_display = ("referrer", "referee_email", "reward_given", "created_at")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "ops_today", "referral_code", "trial_ends_at")
    search_fields = ("user__email", "referral_code")
    readonly_fields = ("api_key", "referral_code")
