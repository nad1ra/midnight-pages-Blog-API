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