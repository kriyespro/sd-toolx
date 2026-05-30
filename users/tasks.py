from celery import shared_task
from django.utils import timezone


@shared_task
def reset_daily_ops():
    from users.models import Profile

    today = timezone.localdate()
    Profile.objects.exclude(ops_reset_date=today).update(
        ops_today=0, ops_reset_date=today
    )
