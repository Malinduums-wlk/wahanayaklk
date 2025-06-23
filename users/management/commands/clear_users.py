from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction

class Command(BaseCommand):
    help = 'Removes all users from the database except superusers'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Delete all non-superuser users
            deleted_count = User.objects.filter(is_superuser=False).delete()[0]
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {deleted_count} users and their associated data')
            ) 