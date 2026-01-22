"""django_webassembly URL Configuration

For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import include, path

from django_webassembly import views

urlpatterns = [
    # Main pages
    path("", views.index, name="index"),
    path("favicon.ico", views.favicon),

    # Admin
    path("admin/", admin.site.urls),

    # Polls app
    path("polls/", include("django_webassembly.polls.urls")),

    # Developer tools
    path("tools/", views.tools, name="tools"),

    # Data API endpoints
    path("api/export/", views.export_data, name="api_export"),
    path("api/import/", views.import_data, name="api_import"),
    path("api/stats/", views.stats, name="api_stats"),
    path("api/reset-votes/", views.reset_votes, name="api_reset_votes"),
]
