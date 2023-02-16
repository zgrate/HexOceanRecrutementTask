from django.conf import settings
from django.db import models
from django.db.models import Model, CharField, IntegerField, ManyToManyField, ManyToOneRel, ForeignKey, OneToOneField


# Create your models here.

class ImageSize(Model):
    width = IntegerField()
    height = IntegerField()


class Tier(Model):
    tier_name = CharField(max_length=50)
    allowed_sizes = ManyToManyField(ImageSize)


class UserInTier(Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tier = OneToOneField(Tier, on_delete=models.CASCADE)



