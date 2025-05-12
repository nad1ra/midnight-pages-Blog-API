from rest_framework import generics, status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, ValidationError
from .models import CustomUser, UserProfile
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
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile = UserProfile.objects.filter(user=self.request.user).first()
        if not profile:
            raise NotFound("User profile not found.")
        return profile



class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)