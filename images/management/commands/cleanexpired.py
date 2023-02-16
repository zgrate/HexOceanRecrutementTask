from django.core.management.base import BaseCommand

from images.models import ExpiringImage


class Command(BaseCommand):
    help = 'Cleans expired images'

    def handle(self, *args, **options):
        ExpiringImage.delete_expired_images()
        self.stdout.write(self.style.SUCCESS("Deleted expired images!"))