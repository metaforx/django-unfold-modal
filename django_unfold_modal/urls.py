"""URL configuration for django-unfold-modal."""

from django.urls import path

from . import views

app_name = "django_unfold_modal"

urlpatterns = [
    path("config.js", views.modal_config_js, name="config_js"),
]
