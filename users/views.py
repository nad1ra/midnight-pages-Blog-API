from rest_framework import generics, status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, ValidationError
from .models import CustomUser, UserProfile
from core.permissions import IsOwner
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


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.AllowAny]


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
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_object(self):
        profile = UserProfile.objects.filter(user=self.request.user).first()
        if not profile:
            raise NotFound("User profile not found.")
        return profile


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





@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def follow_user(request, user_id):
    follower = request.user

    if follower.id == user_id:
        return Response({"message": "You cannot follow yourself!"}, status=status.HTTP_400_BAD_REQUEST)

    user_to_follow = get_object_or_404(CustomUser, id=user_id)
    follower_profile = get_object_or_404(UserProfile, user=follower)

    if user_to_follow in follower_profile.following.all():
        return Response({"message": "You are already following this user!"}, status=status.HTTP_400_BAD_REQUEST)

    follower_profile.following.add(user_to_follow)
    return Response({"message": "Followed successfully!"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unfollow_user(request, user_id):
    follower = request.user
    user_to_unfollow = get_object_or_404(CustomUser, id=user_id)
    follower_profile = get_object_or_404(UserProfile, user=follower)

    if user_to_unfollow not in follower_profile.following.all():
        return Response({"message": "You are not following this user!"}, status=status.HTTP_400_BAD_REQUEST)

    follower_profile.following.remove(user_to_unfollow)
    return Response({"message": "Unfollowed successfully!"}, status=status.HTTP_200_OK)





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
        followers = UserProfile.objects.filter(following=user)
        serializer = UserProfileSerializer(followers, many=True)
        return Response(serializer.data)
