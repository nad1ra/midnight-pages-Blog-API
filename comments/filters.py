import django_filters
from .models import Comment

class CommentFilter(django_filters.FilterSet):
    content = django_filters.CharFilter(lookup_expr='icontains', label="Comment content")
    author = django_filters.CharFilter(field_name='author__username', lookup_expr='icontains', label="Author username")
    post = django_filters.NumberFilter(field_name='post__id', label="Post ID")

    class Meta:
        model = Comment
        fields = ['content', 'author', 'post']
