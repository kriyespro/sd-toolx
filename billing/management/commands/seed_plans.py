from django.core.management.base import BaseCommand

from billing.models import Plan

PLANS = [
    {
        "name": "Free",
        "slug": "free",
        "price_monthly_paise": 0,
        "price_yearly_paise": 0,
        "ops_per_day": 5,
        "max_file_mb": 20,
        "max_files": 3,
        "sort_order": 0,
    },
    {
        "name": "Basic",
        "slug": "basic",
        "price_monthly_paise": 9900,
        "price_yearly_paise": 71280,
        "ops_per_day": 20,
        "max_file_mb": 50,
        "max_files": 5,
        "sort_order": 1,
    },
    {
        "name": "Pro",
        "slug": "pro",
        "price_monthly_paise": 24900,
        "price_yearly_paise": 179280,
        "ops_per_day": -1,
        "max_file_mb": 200,
        "max_files": -1,
        "has_batch": True,
        "has_ai": True,
        "has_esign_unlimited": True,
        "sort_order": 2,
    },
    {
        "name": "Business",
        "slug": "business",
        "price_monthly_paise": 79900,
        "price_yearly_paise": 575280,
        "ops_per_day": -1,
        "max_file_mb": 1024,
        "max_files": -1,
        "has_batch": True,
        "has_ai": True,
        "has_api": True,
        "has_esign_unlimited": True,
        "has_team": True,
        "team_seats": 5,
        "sort_order": 3,
    },
]


class Command(BaseCommand):
    help = "Seed default pricing plans"

    def handle(self, *args, **options):
        for data in PLANS:
            Plan.objects.update_or_create(slug=data["slug"], defaults=data)
        self.stdout.write(self.style.SUCCESS("Plans seeded."))
