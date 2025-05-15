from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser, UserProfile
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework import status
from .filters import UserFilter
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from .services import send_password_reset_email, reset_password_confirm
from core.permissions import IsOwnerOrReadOnly, IsSelf
from .serializers import (
    UserRegisterSerializer,
    VerifyEmailSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    CustomUserSerializer,
    ProfileByUsernameSerializer,
    UserProfileSerializer,
)



class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class EmailVerificationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Email successfully verified."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = CustomUser.objects.get(email=email)
            send_password_reset_email(user)
            return Response({"detail": "A token has been sent for password reset."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            confirm_password = serializer.validated_data['confirm_password']

            try:
                result = reset_password_confirm(token, new_password, confirm_password)
                return Response(result, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsSelf]
    def get_object(self):
        return self.request.user


class ProfileByUsernameView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, username=None):
        profile = UserProfile.objects.filter(user__username=username).first()
        if not profile:
            raise NotFound("Profile not found.")
        serializer = ProfileByUsernameSerializer(profile)
        return Response(serializer.data)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['bio', 'user__username', 'user__email', 'user__first_name', 'user__last_name']
    lookup_field = 'user__username'

    def retrieve(self, request, *args, **kwargs):
        username = self.kwargs.get('user__username')
        if username:
            user_profile = UserProfile.objects.filter(user__username=username).first()
        else:
            user_profile = UserProfile.objects.filter(user=request.user).first()

        if not user_profile:
            raise NotFound(detail="Profile not found.")

        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def follow_user(request, user_id):
    user_to_follow = User.objects.get(id=user_id)
    follower = request.user

    if follower != user_to_follow:
        profile = UserProfile.objects.get(user=follower)

        if user_to_follow not in profile.following.all():
            profile.following.add(user_to_follow)
            user_to_follow.profile.followers.add(follower)


            return Response({"message": "Followed successfully!"}, status=status.HTTP_200_OK)

        return Response({"message": "You are already following this user!"}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "You cannot follow yourself!"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unfollow_user(request, user_id):
    user_to_unfollow = User.objects.get(id=user_id)
    follower = request.user

    profile = UserProfile.objects.get(user=follower)
    if user_to_unfollow in profile.following.all():
        profile.following.remove(user_to_unfollow)
        user_to_unfollow.profile.followers.remove(follower)



        return Response({"message": "Unfollowed successfully!"}, status=status.HTTP_200_OK)

    return Response({"message": "You are not following this user!"}, status=status.HTTP_400_BAD_REQUEST)
  
  
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)