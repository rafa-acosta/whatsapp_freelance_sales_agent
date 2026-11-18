"""WSGI entry point for gunicorn (plan.md, R-017)."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "salesagent.settings.production")
application = get_wsgi_application()
