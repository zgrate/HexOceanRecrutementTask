from django.conf import settings
from django.contrib.auth import models
from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Image(models.Model):
    upload_date = models.DateTimeField()
    original_image = models.ImageField(default="default.jpg")
    image_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, null=True)
    image_type = models.CharField(max_length=50, default="image/*")