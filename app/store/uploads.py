"""Upload path helpers for media files.

User-supplied filenames never reach MEDIA_ROOT: each stored file gets a random
name under a predictable folder, so uploads cannot collide with each other,
cannot overwrite an existing file, and cannot smuggle a path or a script-looking
name into the media tree.

These are referenced by migrations, so keep the names and module path stable.
"""

import re
from pathlib import Path
from uuid import uuid4

from django.utils import timezone

# A plain extension and nothing else — anything odd is dropped rather than stored.
SAFE_SUFFIX = re.compile(r"^\.[A-Za-z0-9]{1,8}$")


def stored_name(filename: str) -> str:
    """Return a random filename that keeps only the original extension."""
    suffix = Path(filename or "").suffix.lower()
    if not SAFE_SUFFIX.match(suffix):
        suffix = ""
    return f"{uuid4().hex}{suffix}"


def service_image_path(instance, filename: str) -> str:
    """services/<year>/<month>/<random>.<ext> — month folders keep directories small.

    Dated rather than slug-based on purpose: renaming a service would otherwise
    strand its image in a folder named after the old slug.
    """
    today = timezone.localdate()
    return f"services/{today:%Y/%m}/{stored_name(filename)}"


def order_item_attachment_path(instance, filename: str) -> str:
    """orders/<order id>/attachments/<random>.<ext> — everything for an order in one place."""
    order_id = instance.order_id or "unassigned"
    return f"orders/{order_id}/attachments/{stored_name(filename)}"
