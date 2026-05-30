"""Tool job tracking models."""
from django.conf import settings
from django.db import models
from django.utils import timezone


class ToolJob(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_DONE = "done"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_FAILED, "Failed"),
        (STATUS_DONE, "Done"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tool_jobs",
    )
    session_key = models.CharField(max_length=40, blank=True, db_index=True)
    tool_slug = models.CharField(max_length=64, db_index=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    input_files = models.JSONField(default=list)
    output_file = models.CharField(max_length=512, blank=True)
    output_url = models.URLField(blank=True, max_length=1024)
    options = models.JSONField(default=dict, blank=True)
    compression_stat = models.JSONField(default=dict, blank=True)
    preview_file = models.CharField(max_length=512, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.tool_slug} — {self.status}"

    def mark_expired(self):
        self.expires_at = timezone.now() + timezone.timedelta(hours=2)


class UsageLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="usage_logs",
    )
    date = models.DateField()
    op_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [("user", "date")]

    def __str__(self):
        return f"{self.user.email} — {self.date}: {self.op_count}"
