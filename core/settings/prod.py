"""Production settings."""
from .base import *  # noqa: F401, F403

DEBUG = False

DATABASES = {"default": env.dj_db_url("DATABASE_URL")}

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

USE_R2 = True
from .storage import *  # noqa: F401, F403

ACCOUNT_EMAIL_VERIFICATION = "mandatory"
