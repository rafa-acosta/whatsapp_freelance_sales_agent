from django.urls import path

from salesagent.whatsapp.views import whatsapp_webhook

urlpatterns = [
    path("webhooks/whatsapp/", whatsapp_webhook, name="whatsapp_webhook"),
]
