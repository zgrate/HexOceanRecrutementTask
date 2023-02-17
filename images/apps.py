from io import BytesIO
from turtledemo.chaos import f

from PIL import Image as PilImg
from django.apps import AppConfig
from django.core.files import File
from django.core.files.storage import default_storage
from django.utils import timezone


DEFAULT_IMAGE = "default.jpg"


class ImagesConfig(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'images'

    def ready(self):
        global DEFAULT_IMAGE

        if not default_storage.exists(DEFAULT_IMAGE):
            temp_io = BytesIO()
            PilImg.new("1", (512, 512)).save(temp_io, "JPEG")
            DEFAULT_IMAGE = default_storage.save(DEFAULT_IMAGE, temp_io)
