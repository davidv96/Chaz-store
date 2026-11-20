from decimal import Decimal

from django.db.models import Avg, Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from orders.models import Order, OrderItem


def get_dashboard_stats(date_from=None, date_to=None):
    queryset = Order.objects.all()
    if date_from:
        queryset = queryset.filter(created_at__gte=date_from)
    if date_to:
        queryset = queryset.filter(created_at__lte=date_to)

    completed_orders = queryset.filter(status=Order.Status.COMPLETED)
    total_revenue = completed_orders.aggregate(total=Sum("total"))["total"] or Decimal("0.00")
    avg_order_value = completed_orders.aggregate(avg=Avg("total"))["avg"] or Decimal("0.00")

    return {
        "total_revenue": total_revenue,
        "total_orders": queryset.count(),
        "pending_orders": queryset.filter(status=Order.Status.PENDING).count(),
        "in_progress_orders": queryset.filter(status=Order.Status.IN_PROGRESS).count(),
        "completed_orders": completed_orders.count(),
        "avg_order_value": avg_order_value,
    }


def get_popular_services(limit=10):
    return (
        OrderItem.objects.values("service__name")
        .annotate(
            order_count=Count("id"),
            total_revenue=Sum("price"),
        )
        .order_by("-order_count")[:limit]
    )


def get_recent_orders(limit=10):
    return Order.objects.select_related("user").order_by("-created_at")[:limit]


def get_revenue_by_month(months=6):
    from dateutil.relativedelta import relativedelta

    start_date = timezone.now() - relativedelta(months=months)
    return (
        Order.objects.filter(
            status=Order.Status.COMPLETED,
            completed_at__gte=start_date,
        )
        .annotate(month=TruncMonth("completed_at"))
        .values("month")
        .annotate(revenue=Sum("total"))
        .order_by("month")
    )
