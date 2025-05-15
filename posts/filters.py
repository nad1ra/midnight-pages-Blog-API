import django_filters
from .models import Post
from users.models import CustomUser


class PostFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label="Title contains")
    author = django_filters.ModelChoiceFilter(queryset=CustomUser.objects.all(), label="Author")
    created_at = django_filters.DateFromToRangeFilter(label="Created Date")

    class Meta:
        model = Post
        fields = ['title', 'author', 'created_at']
