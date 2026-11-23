"""portfolio URL routing for all proposal screens."""

from django.urls import path
from . import views

urlpatterns = [
    # Core proposal screens
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("assets/", views.asset_list_view, name="asset_list"),
    path("assets/add/<str:asset_type>/", views.asset_create_view, name="asset_create"),
    path("assets/<int:asset_id>/", views.asset_detail_view, name="asset_detail"),
    path("analysis/", views.portfolio_analysis_view, name="portfolio_analysis"),
    path("health-score/", views.health_score_detail_view, name="health_score_detail"),
    path("alerts/", views.alerts_list_view, name="alerts_list"),
    path("reports/", views.reports_view, name="reports_view"),
    path("settings/", views.settings_view, name="settings_view"),
]
