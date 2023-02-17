from time import timezone

from django.conf import settings
from django.contrib.auth import models
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# Create your models here.


class Image(models.Model):
    upload_date = models.DateTimeField()
    original_image = models.ImageField(default="default.jpg")
    image_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, null=True)
    image_type = models.CharField(max_length=50, default="image/*")


class ExpiringImage(models.Model):
    image = models.ForeignKey(Image, on_delete=models.RESTRICT)
    expiring_image_uuid = models.CharField(max_length=50)
    creation_date = models.DateTimeField()
    expire_time = models.DateTimeField()

    @staticmethod
    def find_delete_expiring_image(image_id):
        image_filter = ExpiringImage.objects.filter(expiring_image_uuid=image_id)
        if not image_filter.exists():
            return None
        first = image_filter.first()
        if first.expire_time < timezone.now():
            first.delete()
            return None
        return first


    @staticmethod
    def delete_expired_images():
        ExpiringImage.objects.filter(expire_time__lt=timezone.now()).delete()