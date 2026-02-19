"""URL configuration for unfold-modal."""

from django.urls import path

from . import views

app_name = "unfold_modal"

urlpatterns = [
    path("config.js", views.modal_config_js, name="config_js"),
]
