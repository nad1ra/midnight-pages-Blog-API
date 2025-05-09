from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser, UserProfile
from .serializers import CustomUserSerializer, UserProfileSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]

    def retrieve(self, request):
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def retrieve(self, request, username=None):
        if username:
            user_profile = UserProfile.objects.filter(user__username=username).first()
            if not user_profile:
                raise NotFound(detail="Profile not found")
            serializer = UserProfileSerializer(user_profile)
            return Response(serializer.data)

        user_profile = UserProfile.objects.filter(user=request.user).first()
        if not user_profile:
            raise NotFound(detail="User profile not found.")

        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)

