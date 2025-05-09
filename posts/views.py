from rest_framework import viewsets
from .models import Post
from .serializers import PostSerializer
from .pagination import PostPagination


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PostPagination