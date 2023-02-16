from django.contrib import admin
from django.contrib.auth.models import User

from tiers.models import Tier, UserInTier
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


# Register your models here.

class TierInline(admin.StackedInline):
    model = UserInTier
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = (TierInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
