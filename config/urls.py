from django.urls import path
from django.views.debug import default_urlconf

# Serve Django's stock welcome page regardless of DEBUG.
urlpatterns = [path("", default_urlconf)]
