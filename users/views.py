from rest_framework import generics, status, permissions, filters
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from .models import CustomUser, UserProfile
from core.permissions import IsOwnerOrReadOnly
from .services import send_password_reset_email, reset_password_confirm
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
    serializer_class = UserRegisterSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "A verification token has been sent to your emai."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response_data = CustomUserSerializer(user).data
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = CustomUser.objects.get(email=email)
                send_password_reset_email(user)
                return Response({"detail": "A token has been sent for password reset."}, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({"detail": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            password = serializer.validated_data['password']
            password_confirm = serializer.validated_data['password_confirm']

            try:
                result = reset_password_confirm(token, password, password_confirm)
                return Response(result, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

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


class CurrentUserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def get_object(self):
        return get_object_or_404(self.get_queryset())


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def follow_user_by_username(request, username):
    follower = request.user

    if follower.username == username:
        return Response({"message": "You cannot follow yourself!"}, status=status.HTTP_400_BAD_REQUEST)

    user_to_follow = get_object_or_404(CustomUser, username=username)
    user_to_follow_profile = get_object_or_404(UserProfile, user=user_to_follow)
    follower_profile = get_object_or_404(UserProfile, user=follower)

    if user_to_follow_profile in follower_profile.following.all():
        return Response({"message": "You are already following this user!"}, status=status.HTTP_400_BAD_REQUEST)

    follower_profile.following.add(user_to_follow_profile)
    return Response({"message": f"You are now following {username}."}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unfollow_user_by_username(request, username):
    follower = request.user
    user_to_unfollow = get_object_or_404(CustomUser, username=username)
    user_to_unfollow_profile = get_object_or_404(UserProfile, user=user_to_unfollow)
    follower_profile = get_object_or_404(UserProfile, user=follower)

    if user_to_unfollow_profile not in follower_profile.following.all():
        return Response({"message": "You are not following this user!"}, status=status.HTTP_400_BAD_REQUEST)

    follower_profile.following.remove(user_to_unfollow_profile)
    return Response({"message": f"You have unfollowed {username}."}, status=status.HTTP_200_OK)


class FollowingListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, username):
        user = get_object_or_404(CustomUser, username=username)
        profile = get_object_or_404(UserProfile, user=user)
        following = profile.following.all()
        serializer = UserProfileSerializer(following, many=True)
        return Response(serializer.data)


class FollowersListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, username):
        user = get_object_or_404(CustomUser, username=username)
        user_profile = get_object_or_404(UserProfile, user=user)
        followers = UserProfile.objects.filter(following=user_profile)
        serializer = UserProfileSerializer(followers, many=True)
        return Response(serializer.data)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

