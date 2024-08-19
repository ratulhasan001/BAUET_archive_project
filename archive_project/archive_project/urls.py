"""
URL configuration for archive_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from core import views
from posts.views import tag_wise_post
urlpatterns = [
    path('admin/', admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    # path('', HomeView.as_view(), name='homepage'),
    path('',views.home, name = "homepage"),
    path('accounts/', include('accounts.urls')),
    path('posts/', include('posts.urls')),
    path('search/', views.search_posts, name='search_posts'),
    path('dept/<slug:dept_slug>/', views.home, name='dept_wise_post'),
    path('download/<int:post_id>/',views.download_file, name='download_file'),
    path('tag/<slug:tag_slug>/', tag_wise_post, name='tag_wise_post'),


]
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)