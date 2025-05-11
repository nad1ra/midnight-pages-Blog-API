from django.shortcuts import render
from django_filters.views import FilterView
from rest_framework import viewsets
from .models import Post
from .filters import PostFilter
from .serializers import PostSerializer
from .pagination import PostPagination


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PostPagination


class PostListView(FilterView):
    model = Post
    filterset_class = PostFilter
    template_name = 'posts/post_list.html'