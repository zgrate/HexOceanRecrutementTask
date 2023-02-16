from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.models import User

from images.models import Image
from tiers.models import Tier, UserInTier, ImageSize
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


# Register your models here.

class TierInline(admin.StackedInline):
    model = UserInTier
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = (TierInline,)


class ImageSizeInline(admin.TabularInline):
    model = Tier.allowed_sizes.through
    can_delete = False


class ImageSizeAdmin(ModelAdmin):
    inlines = [ImageSizeInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Tier)
admin.site.register(ImageSize)
