from django.contrib import admin

from orders.models import Order, OrderItem, OrderUpdate


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["service", "service_name", "price", "quantity", "notes"]


class OrderUpdateInline(admin.TabularInline):
    model = OrderUpdate
    extra = 0
    readonly_fields = ["created_by", "created_at"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["__str__", "user", "status", "total", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["user__username", "user__email"]
    readonly_fields = ["created_at", "updated_at", "accepted_at", "completed_at"]
    inlines = [OrderItemInline, OrderUpdateInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "service_name", "price", "quantity"]
    list_filter = ["order__status"]


@admin.register(OrderUpdate)
class OrderUpdateAdmin(admin.ModelAdmin):
    list_display = ["order", "message", "created_by", "created_at"]
    list_filter = ["created_at"]
    readonly_fields = ["created_at"]
