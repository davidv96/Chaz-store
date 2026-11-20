from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Prod deploy prep: compile Tailwind CSS, collect static files, then apply migrations."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Building Tailwind CSS..."))
        call_command("tailwind", "build")

        self.stdout.write(self.style.MIGRATE_HEADING("Collecting static files..."))
        call_command("collectstatic", interactive=False, verbosity=0)

        self.stdout.write(self.style.MIGRATE_HEADING("Applying migrations..."))
        call_command("migrate")

        self.stdout.write(self.style.SUCCESS("Deploy prep complete."))
