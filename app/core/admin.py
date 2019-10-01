from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


class UserAdmin(BaseUserAdmin):
    """Custom user admin to override the ordering and list display."""

    ordering = ["id"]
    list_display = ["email", "name"]


admin.site.register(User, UserAdmin)
