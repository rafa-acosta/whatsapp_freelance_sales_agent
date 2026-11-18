"""Recording stand-in for the WhatsApp sender. Synthetic IDs only."""

from salesagent.whatsapp.sender import SendError


class FakeSender:
    def __init__(self):
        self.calls = []
        self.fail_next = 0
        self._counter = 0

    def send_text(self, to_wa_id, text):
        if self.fail_next:
            self.fail_next -= 1
            raise SendError("simulated_failure")
        self.calls.append((to_wa_id, text))
        self._counter += 1
        return f"wamid.TEST{self._counter:06d}"
