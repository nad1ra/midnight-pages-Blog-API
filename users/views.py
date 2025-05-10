from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser, UserProfile
from .serializers import  UserRegisterSerializer, VerifyEmailSerializer, CustomUserSerializer, UserProfileSerializer


class UserRegistrationViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request, *args, **kwargs):
        data = request.data
        user_serializer = self.get_serializer(data=data)

        if user_serializer.is_valid():
            user = user_serializer.save()
            return Response(user_serializer.data, status=201)
        else:
            raise ValidationError(user_serializer.errors)



class EmailVerificationViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'], url_path='verify-email')
    def verify_email(self, request):
        serializer = VerifyEmailSerializer(data=request.data)

        if serializer.is_valid():
            token = serializer.validated_data['token']
            try:
                user = CustomUser.objects.get(verification_token=token)
                user.is_email_verified = True
                user.verification_token = None
                user.save()
                return Response({"detail": "Email successfully verified."}, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='me')
    def get_user(self, request):
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    @action(detail=False, methods=['get'], url_path='<str:username>')
    def get_user_profile_by_username(self, request, username=None):
        if username:
            user_profile = UserProfile.objects.filter(user__username=username).first()
            if not user_profile:
                raise NotFound(detail="Profile not found")
            serializer = UserProfileSerializer(user_profile)
            return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='me')
    def get_profile(self, request):
        user_profile = UserProfile.objects.filter(user=request.user).first()
        if not user_profile:
            raise NotFound(detail="User profile not found.")

        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)

