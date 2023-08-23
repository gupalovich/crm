from ckeditor_uploader.views import browse, upload
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path
from django.views.decorators.cache import never_cache
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    # Ckeditor
    path("ckeditor/upload/", login_required(upload), name="ckeditor_upload"),
    path("ckeditor/browse/", never_cache(login_required(browse)), name="ckeditor_browse"),
    # Auth
    path("api/", include("crm.users.urls", namespace="users")),
    # API
    path("", RedirectView.as_view(url="/api/v1/", permanent=False), name="root"),
    path("api/v1/", include("crm.api.urls", namespace="api")),
    # Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("api-auth/", include("rest_framework.urls")),
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
