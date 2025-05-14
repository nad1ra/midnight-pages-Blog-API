from rest_framework import viewsets, filters
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Comment
from .serializers import CommentSerializer
from .pagination import CommentPagination
from posts.models import Like
from rest_framework import permissions
from core.permissions import IsOwnerOrReadOnly


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer()
    pagination_class = CommentPagination()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['content', 'author__username', 'post__title']

class LikeCommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk=None):
        try:
            comment = Comment.objects.get(id=pk)
            user = request.user
            like, created = Like.objects.get_or_create(comment=comment, user=user)

            if not created:
                return Response({"detail": "You already liked this comment."}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"detail": "Comment liked successfully."}, status=status.HTTP_201_CREATED)
        except Comment.DoesNotExist:
            return Response({"detail": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)


class UnlikeCommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk=None):
        try:
            comment = Comment.objects.get(id=pk)
            user = request.user
            like = Like.objects.get(comment=comment, user=user)
            like.delete()
            return Response({"detail": "Comment unliked successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Like.DoesNotExist:
            return Response({"detail": "You have not liked this comment yet."}, status=status.HTTP_400_BAD_REQUEST)
        except Comment.DoesNotExist:
            return Response({"detail": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)
