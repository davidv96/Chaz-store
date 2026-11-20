from django.urls import path

from orders.views import (
    OrderDetailView,
    OrderListView,
    OwnerOrderCreateView,
    OwnerOrderDetailView,
    OwnerOrderListView,
    RequestOrderCreateView,
    add_order_update,
    add_pending_item,
    quick_create_customer,
    remove_pending_item,
    respond_to_quote,
    set_item_price,
    update_order_status,
)

app_name = "orders"

urlpatterns = [
    path("orders/request/", RequestOrderCreateView.as_view(), name="request_create"),
    path("orders/request/add/<int:service_id>/", add_pending_item, name="add_pending_item"),
    path("orders/request/remove/<int:index>/", remove_pending_item, name="remove_pending_item"),
    path("orders/", OrderListView.as_view(), name="order_list"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
    path("orders/<int:pk>/respond/", respond_to_quote, name="respond_to_quote"),
    path("orders/manage/", OwnerOrderListView.as_view(), name="owner_order_list"),
    path("orders/manage/create/", OwnerOrderCreateView.as_view(), name="owner_order_create"),
    path("orders/manage/customers/create/", quick_create_customer, name="quick_create_customer"),
    path("orders/manage/<int:pk>/", OwnerOrderDetailView.as_view(), name="owner_order_detail"),
    path("orders/manage/<int:pk>/status/", update_order_status, name="update_order_status"),
    path("orders/manage/<int:pk>/update/", add_order_update, name="add_order_update"),
    path("orders/manage/<int:pk>/items/<int:item_pk>/price/", set_item_price, name="set_item_price"),
]
