"""Root URL configuration for AHMS."""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

def landing_page_view(request):
    return render(request, "landing.html")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("portfolio/", include("portfolio.urls")),
    path("", landing_page_view, name="root"),
]
