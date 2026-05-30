"""
Shared Django settings for SD-Toolx.
"""
from pathlib import Path

from environs import Env

env = Env()
env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = env.str("SECRET_KEY", "dev-only-change-in-production")
DEBUG = env.bool("DEBUG", False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", ["localhost", "127.0.0.1"])

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    # Third party
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # Project apps
    "users",
    "dashboard",
    "billing",
    "blog",
    "growth",
    "features.tools",
    "features.api",
    "features.esign",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"

AUTH_USER_MODEL = "users.User"
LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "dashboard:home"
LOGOUT_REDIRECT_URL = "home"

SITE_ID = 1

# Admin at /sd/
ADMIN_URL = "sd/"

# Jinja2 (primary frontend)
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "NAME": "jinja2",
        "OPTIONS": {
            "environment": "core.jinja2.environment",
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_context",
            ],
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Redis
REDIS_URL = env.str("REDIS_URL", "redis://127.0.0.1:6379/0")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "KEY_PREFIX": "sdtoolx",
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Celery
CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_ROUTES = {
    "features.tools.tasks.process_priority": {"queue": "priority"},
    "features.tools.tasks.*": {"queue": "default"},
}
CELERY_BEAT_SCHEDULE = {
    "reset-daily-ops": {
        "task": "users.tasks.reset_daily_ops",
        "schedule": 86400.0,
    },
    "purge-expired-jobs": {
        "task": "features.tools.tasks.purge_expired_jobs",
        "schedule": 3600.0,
    },
}

# django-allauth
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_ADAPTER = "users.adapters.AccountAdapter"
SOCIALACCOUNT_ADAPTER = "users.adapters.SocialAccountAdapter"
SOCIALACCOUNT_AUTO_SIGNUP = True

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Razorpay
RAZORPAY_KEY_ID = env.str("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = env.str("RAZORPAY_KEY_SECRET", "")
RAZORPAY_WEBHOOK_SECRET = env.str("RAZORPAY_WEBHOOK_SECRET", "")

# OpenAI
OPENAI_API_KEY = env.str("OPENAI_API_KEY", "")

# Email
EMAIL_BACKEND = env.str(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = env.str("EMAIL_HOST", "")
EMAIL_PORT = env.int("EMAIL_PORT", 587)
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", "noreply@sdtoolx.com")

# Free tier defaults
FREE_OPS_PER_DAY = 5
FREE_MAX_FILE_MB = 20
FREE_MAX_FILES = 3

# AI tools (Phase 4)
OPENAI_API_KEY = env.str("OPENAI_API_KEY", "")

# Jazzmin admin
JAZZMIN_SETTINGS = {
    "site_title": "SD-Toolx Admin",
    "site_header": "SD-Toolx",
    "site_brand": "SD-Toolx",
    "welcome_sign": "SD-Toolx control panel",
    "copyright": "SD-Toolx",
    "search_model": ["users.User", "features.tools.ToolJob"],
}
