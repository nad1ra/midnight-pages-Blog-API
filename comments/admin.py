from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'author', 'created_at', 'updated_at', 'is_active')
    search_fields = ('id', 'post', 'content', 'author')