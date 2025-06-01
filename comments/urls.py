from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'comments', views.CommentViewSet, basename='comment')

urlpatterns = [
    path('comments/<int:pk>/like/', views.LikeCommentView.as_view(), name='like_comment'),
    path('comments/<int:pk>/unlike/', views.UnlikeCommentView.as_view(), name='unlike_comment'),
    path('posts/<int:post_id>/comments/', views.comment_list, name='post_comments'),
]

urlpatterns += router.urls
