from django.shortcuts import render

from orders.mixins import StaffRequiredMixin
from django.views.generic import TemplateView

from dashboard.services import (
    get_dashboard_stats,
    get_popular_services,
    get_recent_orders,
    get_revenue_by_month,
)


class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stats"] = get_dashboard_stats()
        context["popular_services"] = get_popular_services()
        context["recent_orders"] = get_recent_orders()
        return context


def revenue_chart_partial(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    revenue_data = get_revenue_by_month()
    return render(request, "dashboard/_revenue_chart_partial.html", {
        "revenue_data": revenue_data,
    })


def popular_services_partial(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    popular_services = get_popular_services()
    return render(request, "dashboard/_popular_services_partial.html", {
        "popular_services": popular_services,
    })
