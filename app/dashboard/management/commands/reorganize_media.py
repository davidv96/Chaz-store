"""Move media files that predate the upload-path callables into the current layout.

Dry run by default: nothing is written without --apply.

    python manage.py reorganize_media                    # report only
    python manage.py reorganize_media --apply            # move files, update rows
    python manage.py reorganize_media --apply --prune    # also delete unreferenced files
"""

from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import Service
from orders.models import OrderItem
from store.uploads import order_item_attachment_path, service_image_path

# (model, field name, path callable) — add a row here when a new media field appears.
MEDIA_FIELDS = [
    (Service, "image", service_image_path),
    (OrderItem, "attachment", order_item_attachment_path),
]


class Command(BaseCommand):
    help = "Move existing media into the structure defined by store.uploads."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true", help="Write changes (default: dry run).")
        parser.add_argument(
            "--prune",
            action="store_true",
            help="Delete media files no database row points at. Requires --apply.",
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]
        prune = options["prune"]

        moved, referenced = [], set()

        for model, field, path_for in MEDIA_FIELDS:
            for obj in model.objects.exclude(**{field: ""}).exclude(**{f"{field}__isnull": True}):
                file_field = getattr(obj, field)
                current = file_field.name
                target = path_for(obj, Path(current).name)

                # Already laid out correctly? Leave the name exactly as it is.
                if Path(current).parent == Path(target).parent:
                    referenced.add(current)
                    continue

                if not file_field.storage.exists(current):
                    self.stderr.write(f"missing on disk, skipped: {current}")
                    referenced.add(current)
                    continue

                moved.append((model.__name__, obj.pk, current, target))

                if apply_changes:
                    with file_field.storage.open(current, "rb") as fh:
                        saved = file_field.storage.save(target, ContentFile(fh.read()))
                    with transaction.atomic():
                        setattr(obj, field, saved)
                        obj.save(update_fields=[field])
                    file_field.storage.delete(current)
                    referenced.add(saved)
                else:
                    referenced.add(current)

        verb = "Moved" if apply_changes else "Would move"
        for name, pk, current, target in moved:
            self.stdout.write(f"{verb}: {name}#{pk}  {current} -> {target}")
        if not moved:
            self.stdout.write("All referenced media already in the current layout.")

        # Anything on disk nothing points at — usually a replaced or deleted upload.
        root = Path(settings.MEDIA_ROOT)
        orphans = sorted(
            str(p.relative_to(root))
            for p in root.rglob("*")
            if p.is_file() and str(p.relative_to(root)) not in referenced
        )

        if orphans:
            self.stdout.write(self.style.WARNING(f"\n{len(orphans)} unreferenced file(s):"))
            for name in orphans:
                self.stdout.write(f"  {name}")
            if prune and apply_changes:
                for name in orphans:
                    (root / name).unlink()
                self.stdout.write(self.style.SUCCESS(f"Deleted {len(orphans)} unreferenced file(s)."))
            elif prune:
                self.stdout.write("Pass --apply together with --prune to delete these.")
            else:
                self.stdout.write("Re-run with --apply --prune to delete these.")

        # Leave no empty directories behind after files move out.
        if apply_changes:
            for directory in sorted((p for p in root.rglob("*") if p.is_dir()), reverse=True):
                if not any(directory.iterdir()):
                    directory.rmdir()
                    self.stdout.write(f"Removed empty directory: {directory.relative_to(root)}")
