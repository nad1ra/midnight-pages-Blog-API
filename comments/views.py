from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Comment
from .serializers import CommentSerializer
from .pagination import CommentPagination
from .filters import CommentFilter


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = CommentPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['content', 'author__username', 'post__title']
    filterset_class = CommentFilter
    ordering_fields = ['content', 'author__username', 'post__id']

























































