from django.conf import settings
from django.db import models

from store.uploads import order_item_attachment_path


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending Review"
        QUOTED = "quoted", "Quote Sent"
        ACCEPTED = "accepted", "Accepted"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, help_text="Customer notes for the order")
    admin_notes = models.TextField(blank=True, help_text="Internal notes (not shown to customer)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"Order #{self.pk} - {self.get_status_display()}"

    @property
    def has_pending_pricing(self):
        return self.items.filter(is_price_variable=True, price=0).exists()

    @property
    def has_variable_items(self):
        return self.items.filter(is_price_variable=True).exists()

    @property
    def title(self):
        items = list(self.items.all())
        if not items:
            return f"Order #{self.pk}"
        names = [item.service_name for item in items[:3]]
        result = ", ".join(names)
        if len(items) > 3:
            result += f" +{len(items) - 3} more"
        return result


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    service = models.ForeignKey(
        "catalog.Service", on_delete=models.PROTECT, related_name="order_items", null=True, blank=True,
        help_text="Blank for a freeform customer request with no matching catalog service",
    )
    service_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_price_variable = models.BooleanField(default=False)
    quantity = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True)
    attachment = models.FileField(upload_to=order_item_attachment_path, blank=True)
    reference_url = models.URLField(blank=True, help_text="Link to a Makerworld page or other 3D model repo")

    def __str__(self):
        return f"{self.quantity}x {self.service_name}"

    @property
    def subtotal(self):
        return self.price * self.quantity


class OrderUpdate(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="updates")
    message = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Update on Order #{self.order_id}: {self.message[:50]}"
