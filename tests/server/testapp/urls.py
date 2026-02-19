from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("unfold-modal/", include("unfold_modal.urls")),
]
