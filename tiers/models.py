from django.conf import settings
from django.db import models
from django.db.models import Model, CharField, IntegerField, ManyToManyField, ManyToOneRel, ForeignKey, OneToOneField, \
    BooleanField

from images.utils import is_above_zero, is_above_or_equal_zero


# Create your models here.


class ImageSize(Model):
    height = IntegerField(help_text="Must be above 0px", validators=[is_above_zero], default=0)
    def __str__(self):
        return f"Image of height {self.height}"




class Tier(Model):
    tier_name = CharField(max_length=50, unique=True)
    allowed_sizes = ManyToManyField(ImageSize)
    can_access_original = BooleanField(default=False)
    can_generate_expire_links = BooleanField(default=False)

    def __str__(self):
        return f"{self.tier_name}"

def get_basic_tier():
    return Tier.objects.get_or_create(tier_name=settings.DEFAULT_TIER)[0].id

class UserInTier(Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tier = OneToOneField(Tier, on_delete=models.CASCADE, default=get_basic_tier)



