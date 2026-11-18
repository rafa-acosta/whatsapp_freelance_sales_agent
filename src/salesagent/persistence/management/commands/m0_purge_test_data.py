from django.core.management.base import BaseCommand
from django.db import transaction

from salesagent.persistence.models import Conversation, Message


class Command(BaseCommand):
    help = "Delete M0 test conversations and their messages. Prints counts only (data minimization)."

    def handle(self, *args, **options):
        with transaction.atomic():
            conversations = Conversation.objects.filter(m0_test=True)
            messages = Message.objects.filter(conversation__in=conversations)
            message_count = messages.count()
            conversation_count = conversations.count()
            messages.delete()
            conversations.delete()
        self.stdout.write(f"deleted conversations={conversation_count} messages={message_count}")
