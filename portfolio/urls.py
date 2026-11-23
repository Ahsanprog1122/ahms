"""portfolio URL routing."""

from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("assets/", views.asset_list_view, name="asset_list"),
]
