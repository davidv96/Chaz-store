from django import template

register = template.Library()

STATUS_BADGE_CLASSES = {
    "pending": "badge badge-warning",
    "quoted": "badge badge-secondary",
    "accepted": "badge badge-info",
    "in_progress": "badge badge-primary",
    "completed": "badge badge-success",
    "cancelled": "badge badge-error",
}


@register.filter
def status_badge(status):
    return STATUS_BADGE_CLASSES.get(status, "badge")
