from django.urls import path

from dashboard.views import DashboardView, popular_services_partial, revenue_chart_partial

app_name = "dashboard"

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("dashboard/revenue/", revenue_chart_partial, name="revenue_partial"),
    path("dashboard/popular/", popular_services_partial, name="popular_partial"),
]
