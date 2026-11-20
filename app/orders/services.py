from django.db import transaction
from django.utils import timezone

from orders.models import Order, OrderItem, OrderUpdate


ALLOWED_TRANSITIONS = {
    Order.Status.PENDING: [Order.Status.QUOTED, Order.Status.ACCEPTED, Order.Status.CANCELLED],
    Order.Status.QUOTED: [Order.Status.ACCEPTED, Order.Status.CANCELLED],
    Order.Status.ACCEPTED: [Order.Status.IN_PROGRESS, Order.Status.CANCELLED],
    Order.Status.IN_PROGRESS: [Order.Status.COMPLETED, Order.Status.CANCELLED],
    Order.Status.COMPLETED: [],
    Order.Status.CANCELLED: [],
}


def get_staff_allowed_transitions(order):
    """Transitions staff may trigger themselves.

    Accepting a quote is the customer's call, not staff's — once an order has
    variable-priced items awaiting a quote, staff can only cancel until the
    customer accepts. Orders with no variable pricing skip that gate entirely.
    """
    if order.status == Order.Status.PENDING:
        if order.has_variable_items:
            return [Order.Status.CANCELLED]
        return [Order.Status.ACCEPTED, Order.Status.CANCELLED]
    if order.status == Order.Status.QUOTED:
        return [Order.Status.CANCELLED]
    return ALLOWED_TRANSITIONS.get(order.status, [])


@transaction.atomic
def create_manual_order(user, items, notes="", created_by=None):
    """Create an order manually on behalf of a user.

    items: list of dicts with keys 'service' (Service instance) and 'quantity' (int).
    """
    if not items:
        raise ValueError("Cannot create an order with no items")

    total = sum(
        0 if item["service"].is_price_variable else item["service"].price * item["quantity"]
        for item in items
    )

    order = Order.objects.create(
        user=user,
        total=total,
        notes=notes,
    )

    for item in items:
        service = item["service"]
        OrderItem.objects.create(
            order=order,
            service=service,
            service_name=service.name,
            price=0 if service.is_price_variable else service.price,
            is_price_variable=service.is_price_variable,
            quantity=item["quantity"],
        )

    OrderUpdate.objects.create(
        order=order,
        message="Order created manually by staff",
        created_by=created_by,
    )

    return order


def transition_order_status(order, new_status, user):
    allowed = ALLOWED_TRANSITIONS.get(order.status, [])
    if new_status not in allowed:
        raise ValueError(
            f"Cannot transition from '{order.get_status_display()}' to '{Order.Status(new_status).label}'"
        )

    if new_status == Order.Status.QUOTED and order.has_pending_pricing:
        raise ValueError("Set a price for every item before sending the quote.")

    old_status_display = order.get_status_display()
    order.status = new_status

    if new_status == Order.Status.ACCEPTED:
        order.accepted_at = timezone.now()
    elif new_status == Order.Status.COMPLETED:
        order.completed_at = timezone.now()

    order.save()

    new_status_display = order.get_status_display()
    OrderUpdate.objects.create(
        order=order,
        message=f"Status changed from {old_status_display} to {new_status_display}",
        created_by=user,
    )

    return order
