"""Development settings."""
from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Local file storage in dev (R2 optional)
USE_R2 = env.bool("USE_R2", False)

if not USE_R2:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
else:
    from .storage import *  # noqa: F401, F403

# Disable manifest static files in dev for simpler iteration
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Console email
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Allauth — relaxed in dev
ACCOUNT_EMAIL_VERIFICATION = "none"

# Dev: no Redis required for runserver
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "sdtoolx-dev",
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# Run Celery tasks inline in dev (no Redis required)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Google OAuth — enable when credentials are set
if env.str("GOOGLE_CLIENT_ID", ""):
    INSTALLED_APPS += [
        "allauth.socialaccount.providers.google",
    ]
    SOCIALACCOUNT_PROVIDERS = {
        "google": {
            "APP": {
                "client_id": env.str("GOOGLE_CLIENT_ID"),
                "secret": env.str("GOOGLE_CLIENT_SECRET"),
                "key": "",
            },
            "SCOPE": ["profile", "email"],
            "AUTH_PARAMS": {"access_type": "online"},
        }
    }
