"""Base settings. Every value comes from the environment (FR-048, R-007).

No region, credential, API key, or phone number is hardcoded here.
"""

from __future__ import annotations

import os
from pathlib import Path

from salesagent.settings.secrets import SecretValue

BASE_DIR = Path(__file__).resolve().parents[3]


def env(name: str, default: str | None = None) -> str:
    value = os.environ.get(name)
    if value is None:
        if default is None:
            return ""
        return default
    return value


def env_bool(name: str, default: bool = False) -> bool:
    return env(name, "true" if default else "false").strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str) -> list[str]:
    return [item.strip() for item in env(name).split(",") if item.strip()]


SALESAGENT_ENV = env("SALESAGENT_ENV", "development")

SECRET_KEY = SecretValue(env("DJANGO_SECRET_KEY")).get()
DEBUG = env_bool("DJANGO_DEBUG", False)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS")

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "salesagent.persistence",
    "salesagent.orchestration",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "salesagent.urls"
USE_TZ = True
TIME_ZONE = "UTC"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("SALESAGENT_DB_NAME", "salesagent"),
        "USER": env("SALESAGENT_DB_USER", "salesagent"),
        "PASSWORD": SecretValue(env("SALESAGENT_DB_PASSWORD")).get(),
        "HOST": env("SALESAGENT_DB_HOST", "localhost"),
        "PORT": env("SALESAGENT_DB_PORT", "5432"),
    }
}

# Keyed hashing of identifiers in logs and in the M0 allowlist (R-018).
LOG_HMAC_KEY = SecretValue(env("SALESAGENT_LOG_HMAC_KEY"))

# WhatsApp Business Platform Cloud API (R-004). Values are supplied by the owner.
WHATSAPP_APP_SECRET = SecretValue(env("WHATSAPP_APP_SECRET"))
WHATSAPP_VERIFY_TOKEN = SecretValue(env("WHATSAPP_VERIFY_TOKEN"))
WHATSAPP_ACCESS_TOKEN = SecretValue(env("WHATSAPP_ACCESS_TOKEN"))
WHATSAPP_PHONE_NUMBER_ID = env("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_GRAPH_API_VERSION = env("WHATSAPP_GRAPH_API_VERSION")
WHATSAPP_GRAPH_BASE_URL = env("WHATSAPP_GRAPH_BASE_URL", "https://graph.facebook.com")

# M0 technical connectivity mode (plan M0; tasks T127 and T132). Off by default.
WHATSAPP_M0_MODE = env_bool("WHATSAPP_M0_MODE", False)
# Keyed hashes (HMAC with LOG_HMAC_KEY) of the synthetic test numbers allowed in M0.
WHATSAPP_TEST_RECIPIENT_HMACS = env_list("WHATSAPP_TEST_RECIPIENT_HMACS")
WHATSAPP_M0_RESPONSE_TEXT = env("WHATSAPP_M0_RESPONSE_TEXT", "Connectivity test OK")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
}
