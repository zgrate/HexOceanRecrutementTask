from django.core.files.storage import default_storage
from django.core.management import BaseCommand

from images.models import Image


class Command(BaseCommand):
    help = 'Cleans cached images images'

    def handle(self, *args, **options):

        dirs, files = default_storage.listdir("")
        for file in files:
            i = Image.objects.filter(original_image=file)
            if not i.exists():
                default_storage.delete(file)
        self.stdout.write(self.style.SUCCESS("Deleted expired images!"))