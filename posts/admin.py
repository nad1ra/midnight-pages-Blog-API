from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'is_active', 'created_at', 'updated_at')
    search_fields = ('title', 'author', 'content')