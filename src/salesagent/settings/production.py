"""Production settings. Hardening only; the full readiness gate is task T142."""

from salesagent.settings.base import *  # noqa: F401,F403
from salesagent.settings.base import WHATSAPP_M0_MODE, SALESAGENT_ENV

if SALESAGENT_ENV == "production" and WHATSAPP_M0_MODE:
    raise RuntimeError("WHATSAPP_M0_MODE must be off in production (T142 readiness gate).")

DEBUG = False
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
