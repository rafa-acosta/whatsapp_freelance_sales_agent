import urllib.request

import pytest

from salesagent.whatsapp import sender
from tests.fixtures.whatsapp.fake_sender import FakeSender


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    """No test may reach the network. Any attempt fails the test."""

    def _blocked(*args, **kwargs):
        raise AssertionError("network access attempted during tests")

    monkeypatch.setattr(urllib.request, "urlopen", _blocked)


@pytest.fixture
def fake_sender(monkeypatch):
    fake = FakeSender()
    monkeypatch.setattr(sender, "send_text", fake.send_text)
    return fake
