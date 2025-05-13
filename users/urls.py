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

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views


urlpatterns = [
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('auth/email-verify/', views.EmailVerificationView.as_view(), name='verification'),
    path('auth/login/', TokenObtainPairView.as_view(), name='log-in'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/logout/', views.LogoutView.as_view(), name='auth_logout'),
    path('auth/password-reset/', views.PasswordResetRequestView.as_view(), name='password-reset'),
    path('auth/password-confirm/', views.PasswordResetConfirmView.as_view(), name='password-confirm'),
    path('users/me/', views.CurrentUserView.as_view(), name='get-user'),
    path('profiles/me/', views.CurrentUserProfileView.as_view(), name='get-update-profile'),
    path('profiles/<str:username>/', views.ProfileByUsernameView.as_view(), name='password-confirm'),
]