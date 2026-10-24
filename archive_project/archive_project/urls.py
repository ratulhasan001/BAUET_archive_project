from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="homepage"),
    path("dept/<slug:dept_slug>/", views.home, name="dept_wise_post"),
    path("tag/<slug:tag_slug>/", views.home, name="tag_wise_post"),
    path("search/", views.search_posts, name="search_posts"),
    path("download/<int:post_id>/", views.download_file, name="download_file"),
    path("accounts/", include("accounts.urls")),
    path("posts/", include("posts.urls")),
]

if settings.DEBUG:
    urlpatterns += [path("__reload__/", include("django_browser_reload.urls"))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
