from django.urls import path

from config.views import welcome

urlpatterns = [path("", welcome)]
