from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path

from unfold_modal.utils import get_cms_modal_head_html


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


def cms_modal_host_view(request):
    """Serve a page that simulates Django CMS modal hosting admin in an iframe."""
    admin_url = request.GET.get("url", "/admin/")
    cms_head = get_cms_modal_head_html()
    html = f"""<!DOCTYPE html>
<html>
<head>
<title>CMS Modal Host</title>
{cms_head}
</head>
<body>
<div class="cms-modal cms-modal-open cms-modal-iframe">
  <div class="cms-modal-body">
    <div class="cms-modal-frame">
      <iframe id="cms-iframe" src="{admin_url}" style="width:100%;height:80vh;border:none;"></iframe>
    </div>
  </div>
</div>
</body>
</html>"""
    return HttpResponse(html)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("unfold-modal/", include("unfold_modal.urls")),
    path("iframe-host/", iframe_host_view, name="iframe_host"),
    path("cms-modal-host/", cms_modal_host_view, name="cms_modal_host"),
]
