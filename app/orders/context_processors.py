from orders.cart import count


def cart_item_count(request):
    return {"cart_item_count": count(request)}
