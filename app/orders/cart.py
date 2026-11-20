"""Session-backed cart of pending line items, staged before a request is submitted.

Works for anonymous visitors too — the session persists across login, so
items added while browsing carry over once the customer signs in to submit.
"""

SESSION_KEY = "pending_order_items"


def get_items(request):
    return request.session.get(SESSION_KEY, [])


def add_item(request, item_name, description="", base_price=None):
    items = get_items(request)
    items.append({"item_name": item_name, "description": description, "base_price": base_price})
    request.session[SESSION_KEY] = items


def remove_item(request, index):
    items = get_items(request)
    if 0 <= index < len(items):
        items.pop(index)
        request.session[SESSION_KEY] = items


def clear(request):
    request.session.pop(SESSION_KEY, None)


def count(request):
    return len(get_items(request))
