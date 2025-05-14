from django.contrib import admin
from .models import Notification


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'verb', 'is_read', 'time')
    list_filter = ('is_read', 'time')
    search_fields = ('user__username', 'verb')
    ordering = ('-time',)
    list_per_page = 20

admin.site.register(Notification, NotificationAdmin)
