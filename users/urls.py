from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views as jwt_views
from .views import UserViewSet, UserProfileViewSet, UserRegistrationViewSet

router = DefaultRouter()
router.register(r'auth', UserRegistrationViewSet, basename='authentication')
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', UserProfileViewSet, basename='profile')


urlpatterns = [
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token-refresh'),
    path('' , include(router.urls)),
]