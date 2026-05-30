from django.core.management.base import BaseCommand
from django.utils import timezone

from billing.models import Plan
from users.models import User


class Command(BaseCommand):
    help = "Create test user from test_user.txt"

    def handle(self, *args, **options):
        email = "test@sdtoolx.com"
        password = "Test@1234"
        pro_plan = Plan.objects.filter(slug="pro").first()

        user, created = User.objects.get_or_create(email=email, defaults={"is_active": True})
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created user {email}"))
        else:
            user.set_password(password)
            user.save()
            self.stdout.write(f"Updated password for {email}")

        profile = user.profile
        if pro_plan:
            profile.plan = pro_plan
        profile.trial_ends_at = timezone.now() + timezone.timedelta(days=7)
        profile.save()
        self.stdout.write(self.style.SUCCESS("Test user ready (Pro trial 7 days)."))
