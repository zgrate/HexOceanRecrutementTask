from django.core.files.storage import default_storage
from django.core.management import BaseCommand


def rm(dir):
    dirs, files = default_storage.listdir(dir)
    for file in files:
        default_storage.delete(f'{dir}/{file}')
    for directory in dirs:
        rm(directory)


class Command(BaseCommand):
    help = 'Cleans cached images images'

    def handle(self, *args, **options):
        if default_storage.exists("temp"):
            rm("temp")
        self.stdout.write(self.style.SUCCESS("Deleted cached images!"))
