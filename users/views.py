from rest_framework import viewsets, filters
from rest_framework import generics, permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, ValidationError
from .models import CustomUser, UserProfile
from django.contrib.auth.models import User
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



class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'role']



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


class CurrentUserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['bio', 'user__username', 'user__email', 'user__first_name', 'user__last_name']
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self):
        profile = UserProfile.objects.filter(user=self.request.user).first()
        if not profile:
            raise NotFound("User profile not found.")
        return profile




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
