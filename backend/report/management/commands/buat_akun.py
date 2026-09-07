import os

from django.core.management.base import BaseCommand, CommandError

from report.models import User

AKUN = [
    {"username": "clyde", "first_name": "Clyde", "role": User.Role.SUPERUSER,
     "no_hp": "081200000001", "is_superuser": True, "is_staff": True},
    {"username": "devy", "first_name": "Devy", "role": User.Role.ADMIN,
     "no_hp": "081200000002", "is_staff": True},
    {"username": "mia", "first_name": "Mia", "role": User.Role.ADMIN,
     "no_hp": "081200000003", "is_staff": True},
    {"username": "utoro", "first_name": "Utoro RW", "last_name": "Adjie", "role": User.Role.SALES,
     "no_hp": "081200000004"},
    {"username": "maryadi", "first_name": "Maryadi", "role": User.Role.SALES,
     "no_hp": "081200000005"},
]


class Command(BaseCommand):
    help = "Membuat akun awal (Clyde, Devy, Mia, Utoro RW Adjie, Maryadi). Idempotent."

    def add_arguments(self, parser):
        parser.add_argument("--password", help="Password default (fallback env DEFAULT_PASSWORD)")
        parser.add_argument("--reset", action="store_true", help="Reset password akun yang sudah ada")

    def handle(self, *args, **options):
        password = options["password"] or os.environ.get("DEFAULT_PASSWORD")
        if not password:
            raise CommandError("Password wajib: gunakan --password atau env DEFAULT_PASSWORD.")
        for data in AKUN:
            data = dict(data)
            username = data.pop("username")
            user, created = User.objects.get_or_create(username=username, defaults=data)
            if created or options["reset"]:
                user.set_password(password)
            for key, val in data.items():
                setattr(user, key, val)
            user.save()
            label = "dibuat" if created else "sudah ada"
            self.stdout.write(self.style.SUCCESS(f"{user.username:10s} {user.get_role_display():12s} {label}"))
