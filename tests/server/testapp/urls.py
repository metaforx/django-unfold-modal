from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path


def iframe_host_view(request):
    """Serve a page that embeds admin in an iframe (simulates CMS sideframe)."""
    admin_url = request.GET.get("url", "/admin/")
    html = f"""<!DOCTYPE html>
<html>
<head><title>Iframe Host</title></head>
<body>
<iframe id="sideframe" src="{admin_url}" style="width:100%;height:90vh;border:none;"></iframe>
</body>
</html>"""
    return HttpResponse(html)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("unfold-modal/", include("unfold_modal.urls")),
    path("iframe-host/", iframe_host_view, name="iframe_host"),
]
