from rest_framework import viewsets, filters
from .models import Comment
from .serializers import CommentSerializer
from .pagination import CommentPagination


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer()
    pagination_class = CommentPagination()
    filter_backends = [filters.SearchFilter]
    search_fields = ['content', 'author__username', 'post__title']
