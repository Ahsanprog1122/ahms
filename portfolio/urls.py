"""portfolio URL routing."""

from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("assets/add/<str:asset_type>/", views.asset_create_view, name="asset_create"),
    path("assets/<int:asset_id>/", views.asset_detail_view, name="asset_detail"),
]
