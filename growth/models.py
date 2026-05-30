"""Growth app models — URL shortener, social proof."""
from django.db import models


class ShortLink(models.Model):
    code = models.CharField(max_length=16, unique=True, db_index=True)
    target_url = models.URLField(max_length=2048)
    click_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.code} → {self.target_url[:50]}"
