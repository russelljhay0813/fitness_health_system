from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Health Info', {'fields': ('role', 'height', 'date_of_birth')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserProfile)