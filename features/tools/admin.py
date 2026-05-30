from django.contrib import admin

from features.tools.models import ToolJob, UsageLog


@admin.register(ToolJob)
class ToolJobAdmin(admin.ModelAdmin):
    list_display = ("id", "tool_slug", "status", "user", "created_at")
    list_filter = ("tool_slug", "status")
    search_fields = ("user__email", "session_key")


@admin.register(UsageLog)
class UsageLogAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "op_count")
