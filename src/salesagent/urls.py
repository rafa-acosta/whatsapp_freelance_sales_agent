from django.urls import include, path

urlpatterns = [
    path("", include("salesagent.whatsapp.urls")),
]
