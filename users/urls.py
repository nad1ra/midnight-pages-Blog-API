from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views as jwt_views
from .views import UserViewSet, UserProfileViewSet, follow_user, unfollow_user


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', UserProfileViewSet, basename='profile')


urlpatterns = [
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token-refresh'),
    path('users/me/', UserViewSet.as_view({'get': 'retrieve'}), name='user-data'),
    path('profiles/me/', UserProfileViewSet.as_view({'get': 'retrieve'}), name='user-profile'),
    path('profiles/<str:username>/', UserProfileViewSet.as_view({'get': 'retrieve'}), name='profile-by-username'),
    path('follow/<int:user_id>/', follow_user, name='follow-user'),
    path('unfollow/<int:user_id>/', unfollow_user, name='unfollow-user'),
    path('' , include(router.urls)),
]