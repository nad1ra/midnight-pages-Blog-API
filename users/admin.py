from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = ('username', 'email', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')


    readonly_fields = ('date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        (None, {
            'fields': ('role', 'verification_token', 'is_verified'),
        }),
    )
