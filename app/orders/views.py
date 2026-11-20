from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, View

from django.contrib.auth.mixins import LoginRequiredMixin

from catalog.models import Service
from orders import cart
from orders.forms import RequestItemFormSet
from orders.mixins import StaffRequiredMixin
from orders.models import Order, OrderItem, OrderUpdate
from orders.services import (
    create_manual_order,
    get_staff_allowed_transitions,
    transition_order_status,
)


# ── Customer Views ──────────────────────────────────────────────────────────────


class RequestOrderCreateView(View):
    """Simple freeform request form: no catalog browsing, just describe what you want.

    Viewing and editing the cart of pending items needs no account — only
    actually submitting the request does, so guests can add items and review
    them here before being asked to log in.
    """

    template_name = "orders/request_create.html"

    def get(self, request):
        pending_items = cart.get_items(request)
        initial = [
            {
                "item_name": item["item_name"],
                "description": item["description"],
                "base_price": item.get("base_price"),
            }
            for item in pending_items
        ]
        formset = RequestItemFormSet(prefix="items", initial=initial or None)
        return render(request, self.template_name, {"formset": formset, "pending_count": len(pending_items)})

    def post(self, request):
        if not request.user.is_authenticated:
            login_url = f"{resolve_url(settings.LOGIN_URL)}?next={request.path}"
            messages.info(request, "Log in to submit your request — your items are saved.")
            return redirect(login_url)

        formset = RequestItemFormSet(request.POST, request.FILES, prefix="items")
        if formset.is_valid():
            order = Order.objects.create(
                user=request.user,
                total=0,
                notes=request.POST.get("notes", "").strip(),
            )
            for form in formset:
                item_name = form.cleaned_data.get("item_name")
                if not item_name:
                    continue
                matched_service = Service.objects.filter(name__iexact=item_name, is_active=True).first()
                OrderItem.objects.create(
                    order=order,
                    service=matched_service,
                    service_name=item_name,
                    price=0,
                    is_price_variable=True,
                    quantity=form.cleaned_data.get("quantity") or 1,
                    notes=form.cleaned_data.get("description", ""),
                    attachment=form.cleaned_data.get("image") or "",
                    reference_url=form.cleaned_data.get("reference_url", ""),
                )
            OrderUpdate.objects.create(order=order, message="Request submitted", created_by=request.user)
            cart.clear(request)
            messages.success(request, "Request submitted! We'll review it and follow up with pricing.")
            return redirect("orders:order_detail", pk=order.pk)
        if request.FILES:
            messages.warning(request, "Please re-attach any photos above — they don't carry over when fixing errors below.")
        return render(request, self.template_name, {"formset": formset})


@require_POST
def add_pending_item(request, service_id):
    """Stash a catalog service as a prefilled line item for the freeform request form.

    No login required — the cart lives in the session and carries over once
    the customer signs in to actually submit the request.
    """
    service = get_object_or_404(Service, pk=service_id, is_active=True)
    cart.add_item(
        request,
        item_name=service.name,
        description=f"Custom {service.name} order — please add size, color/material, and any personalization details here.",
        base_price=None if service.is_price_variable else str(service.price),
    )
    messages.success(request, f'"{service.name}" added to your order request.')

    referer = request.META.get("HTTP_REFERER", "")
    if url_has_allowed_host_and_scheme(referer, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return redirect(referer)
    return redirect("catalog:home")


@require_POST
def remove_pending_item(request, index):
    """Drop an item from the session cart by its position — a real removal, not just a UI hide."""
    cart.remove_item(request, index)
    return redirect("orders:request_create")


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order_items"] = self.object.items.all()
        context["updates"] = self.object.updates.order_by("created_at")
        return context


@require_POST
@login_required
def respond_to_quote(request, pk):
    """Customer accepts or declines a staff-sent quote before work can begin."""
    order = get_object_or_404(Order, pk=pk, user=request.user)
    action = request.POST.get("action")
    if order.status != Order.Status.QUOTED or action not in ("accept", "decline"):
        raise PermissionDenied

    new_status = Order.Status.ACCEPTED if action == "accept" else Order.Status.CANCELLED
    try:
        transition_order_status(order, new_status, request.user)
    except ValueError as e:
        messages.error(request, str(e))
    else:
        messages.success(request, "Quote accepted — we'll get started!" if action == "accept" else "Order cancelled.")
    return redirect("orders:order_detail", pk=order.pk)


# ── Owner Views ─────────────────────────────────────────────────────────────────


class OwnerOrderListView(StaffRequiredMixin, ListView):
    model = Order
    template_name = "orders/owner/order_list.html"
    context_object_name = "orders"
    paginate_by = 20

    def get_queryset(self):
        queryset = Order.objects.select_related("user").prefetch_related("items").all()
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_template_names(self):
        if hasattr(self.request, "htmx") and self.request.htmx:
            return ["orders/owner/_order_list_partial.html"]
        return [self.template_name]


class OwnerOrderDetailView(StaffRequiredMixin, DetailView):
    model = Order
    template_name = "orders/owner/order_detail.html"
    context_object_name = "order"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order_items"] = self.object.items.all()
        context["updates"] = self.object.updates.order_by("created_at")
        context["allowed_transitions"] = self._get_allowed_transitions()
        return context

    def _get_allowed_transitions(self):
        return get_staff_allowed_transitions(self.object)


def _require_staff(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        raise PermissionDenied


@require_POST
def update_order_status(request, pk):
    _require_staff(request)
    order = get_object_or_404(Order, pk=pk)
    new_status = request.POST.get("status", "")

    if new_status not in get_staff_allowed_transitions(order):
        return render(request, "orders/owner/_status_controls_partial.html", {
            "order": order,
            "allowed_transitions": get_staff_allowed_transitions(order),
            "error": "That status change isn't available.",
        })

    try:
        transition_order_status(order, new_status, request.user)
    except ValueError as e:
        return render(request, "orders/owner/_status_controls_partial.html", {
            "order": order,
            "allowed_transitions": get_staff_allowed_transitions(order),
            "error": str(e),
        })

    return render(request, "orders/owner/_status_controls_partial.html", {
        "order": order,
        "allowed_transitions": get_staff_allowed_transitions(order),
    })


@require_POST
def add_order_update(request, pk):
    _require_staff(request)
    order = get_object_or_404(Order, pk=pk)
    message = request.POST.get("message", "").strip()
    if message:
        OrderUpdate.objects.create(
            order=order,
            message=message,
            created_by=request.user,
        )
    updates = order.updates.order_by("created_at")
    return render(request, "orders/_order_timeline_partial.html", {
        "order": order,
        "updates": updates,
    })


class OwnerOrderCreateView(StaffRequiredMixin, View):
    template_name = "orders/owner/order_create.html"

    def get(self, request):
        from catalog.models import Service
        users = get_user_model().objects.order_by("email")
        services = Service.objects.filter(is_active=True).prefetch_related("tags")
        return render(request, self.template_name, {"users": users, "services": services})

    def post(self, request):
        from catalog.models import Service
        user_id = request.POST.get("user")
        notes = request.POST.get("notes", "").strip()

        User = get_user_model()
        users = User.objects.order_by("email")
        services = Service.objects.filter(is_active=True).prefetch_related("tags")

        if not user_id:
            return render(request, self.template_name, {
                "users": users, "services": services, "error": "Please select a customer."
            })

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return render(request, self.template_name, {
                "users": users, "services": services, "error": "Customer not found."
            })

        items = []
        for service in services:
            qty_str = request.POST.get(f"qty_{service.pk}", "").strip()
            if qty_str:
                try:
                    qty = int(qty_str)
                    if qty > 0:
                        items.append({"service": service, "quantity": qty})
                except ValueError:
                    pass

        if not items:
            return render(request, self.template_name, {
                "users": users, "services": services,
                "error": "Please add at least one service.",
                "selected_user": user_id,
                "notes": notes,
            })

        order = create_manual_order(user, items, notes=notes, created_by=request.user)
        return redirect("orders:owner_order_detail", pk=order.pk)


@require_POST
def quick_create_customer(request):
    _require_staff(request)
    email = request.POST.get("email", "").strip()

    User = get_user_model()
    error = None
    new_user = None

    if not email:
        error = "Email is required."
    elif User.objects.filter(email=email).exists():
        error = f"A customer with email '{email}' already exists."
    else:
        from django.utils.crypto import get_random_string
        new_user = User.objects.create_user(
            email=email,
            password=get_random_string(24),
        )

    users = User.objects.order_by("email")
    return render(request, "orders/owner/_quick_customer_partial.html", {
        "users": users,
        "new_user": new_user,
        "error": error,
    })


@require_POST
def set_item_price(request, pk, item_pk):
    _require_staff(request)
    order = get_object_or_404(Order, pk=pk)
    item = get_object_or_404(OrderItem, pk=item_pk, order=order)

    try:
        from decimal import Decimal, InvalidOperation
        price = Decimal(request.POST.get("price", "").strip())
        if price < 0:
            raise ValueError
    except (InvalidOperation, ValueError):
        return render(request, "orders/owner/_order_items_card_partial.html", {
            "order": order,
            "order_items": order.items.all(),
            "price_error": item_pk,
        })

    item.price = price
    item.save()

    order.total = sum(i.subtotal for i in order.items.all())
    order.save()

    if order.status == Order.Status.PENDING and not order.has_pending_pricing:
        transition_order_status(order, Order.Status.QUOTED, request.user)

    return render(request, "orders/owner/_set_price_response_partial.html", {
        "order": order,
        "order_items": order.items.all(),
        "allowed_transitions": get_staff_allowed_transitions(order),
    })
