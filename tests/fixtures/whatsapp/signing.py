"""Signs synthetic bodies with the test app secret, as Meta does (HMAC-SHA256)."""

from django.conf import settings

from salesagent.whatsapp.signature import compute_signature


def sign(raw_body: bytes) -> str:
    return compute_signature(raw_body, settings.WHATSAPP_APP_SECRET.get())
