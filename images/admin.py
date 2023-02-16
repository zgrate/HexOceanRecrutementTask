from django.contrib import admin

from images.models import Image, ExpiringImage

# Register your models here.
admin.site.register(Image)
admin.site.register(ExpiringImage)