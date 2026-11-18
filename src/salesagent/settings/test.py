"""Test settings. Synthetic values only; tests make no network calls.

Synthetic test numbers use the reserved 555-01xx range and are never real customers.
"""

from salesagent.logging.masking import hmac_identifier
from salesagent.settings.base import *  # noqa: F401,F403
from salesagent.settings.secrets import SecretValue

DEBUG = False
SALESAGENT_ENV = "test"
SECRET_KEY = "test-only-not-a-secret"  # noqa: S105 - synthetic test value
ALLOWED_HOSTS = ["testserver", "localhost"]

_TEST_LOG_KEY = "test-log-hmac-key"
LOG_HMAC_KEY = SecretValue(_TEST_LOG_KEY)
WHATSAPP_APP_SECRET = SecretValue("test-app-secret")
WHATSAPP_VERIFY_TOKEN = SecretValue("test-verify-token")
WHATSAPP_ACCESS_TOKEN = SecretValue("test-access-token")
WHATSAPP_PHONE_NUMBER_ID = "test-phone-number-id"
WHATSAPP_GRAPH_API_VERSION = "v-test"

WHATSAPP_M0_MODE = True
TEST_ALLOWED_WA_ID = "15555550100"
TEST_OTHER_WA_ID = "15555550199"
WHATSAPP_TEST_RECIPIENT_HMACS = [hmac_identifier(TEST_ALLOWED_WA_ID, _TEST_LOG_KEY)]
WHATSAPP_M0_RESPONSE_TEXT = "Connectivity test OK"
