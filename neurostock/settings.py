import os
from pathlib import Path
from datetime import timedelta

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ImproperlyConfigured(
            f"Set {name} in the environment or in a .env file at the project root."
        )
    return value


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.lower() in ("1", "true", "yes", "on")


# ── Core ──────────────────────────────────────────────────────────────────────

SECRET_KEY = _require_env("DJANGO_SECRET_KEY")
DEBUG = _env_bool("DJANGO_DEBUG", default=False)
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

_hosts = os.environ.get("DJANGO_ALLOWED_HOSTS", "").strip()
ALLOWED_HOSTS = [h.strip() for h in _hosts.split(",") if h.strip()]

# ── JWT ───────────────────────────────────────────────────────────────────────
# Use a dedicated JWT secret so rotating it doesn't invalidate the Django secret.
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)
JWT_ACCESS_TOKEN_EXPIRY = timedelta(hours=2)
JWT_REFRESH_TOKEN_EXPIRY = timedelta(days=7)
PASSWORD_RESET_TOKEN_EXPIRY = timedelta(minutes=15)

# ── Installed Apps ────────────────────────────────────────────────────────────

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    # Domain apps
    "apps.auth.apps.NeuroAuthConfig",
    "apps.inventory.apps.InventoryConfig",
    "apps.transactions.apps.TransactionsConfig",
    "apps.billing.apps.BillingConfig",
    "apps.analytics.apps.AnalyticsConfig",
    "apps.notifications.apps.NotificationsConfig",
]

# ── Middleware ─────────────────────────────────────────────────────────────────

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "neurostock.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "neurostock.wsgi.application"

# ── Database ──────────────────────────────────────────────────────────────────

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": _require_env("POSTGRES_DB"),
        "USER": _require_env("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": _require_env("POSTGRES_HOST"),
        "PORT": _require_env("POSTGRES_PORT"),
        "CONN_MAX_AGE": 60,
        "OPTIONS": {
            "connect_timeout": 10,
        },
    }
}

# ── DRF ───────────────────────────────────────────────────────────────────────

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "common.auth.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "common.auth.IsAuthenticated",
    ],
    "EXCEPTION_HANDLER": "common.exception_handler.custom_exception_handler",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

# ── CORS ──────────────────────────────────────────────────────────────────────

CORS_ALLOW_ALL_ORIGINS = DEBUG  # restrict to specific origins in production
CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    if o.strip()
]

# ── Static files ──────────────────────────────────────────────────────────────

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# ── Internationalisation ──────────────────────────────────────────────────────

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ── Logging ───────────────────────────────────────────────────────────────────

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "app.log",
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console", "file"],
            "level": "ERROR",
            "propagate": False,
        },
        "common": {
            "handlers": ["console", "file"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "services": {
            "handlers": ["console", "file"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "repositories": {
            "handlers": ["console", "file"],
            "level": "DEBUG" if DEBUG else "WARNING",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console", "file"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
    },
}
