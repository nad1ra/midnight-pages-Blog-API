from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('auth/verify-email/', views.EmailVerificationView.as_view(), name='email-verification'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/password-reset/', views.PasswordResetRequestView.as_view(), name='password-reset'),
    path('auth/password-confirm/', views.PasswordResetConfirmView.as_view(), name='password-confirm'),
    path('users/me/', views.CurrentUserView.as_view(), name='current-user'),
    path('profiles/me/', views.CurrentUserProfileView.as_view(), name='current-user-profile'),
    path('profiles/<str:username>/', views.ProfileByUsernameView.as_view(), name='profile-by-username'),
    path('users/<int:user_id>/follow/', views.follow_user, name='follow-user'),
    path('users/<int:user_id>/unfollow/', views.unfollow_user, name='unfollow-user'),
    path('profiles/<str:username>/following/', views.FollowingListView.as_view(), name='following-list'),
    path('profiles/<str:username>/followers/', views.FollowersListView.as_view(), name='followers-list'),

]
