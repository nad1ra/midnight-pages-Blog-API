from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser, UserProfile
from .serializers import CustomUserSerializer, UserProfileSerializer
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework import status



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


@api_view(['POST'])
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
def unfollow_user(request, user_id):
    user_to_unfollow = User.objects.get(id=user_id)
    follower = request.user

    profile = UserProfile.objects.get(user=follower)
    if user_to_unfollow in profile.following.all():
        profile.following.remove(user_to_unfollow)
        user_to_unfollow.profile.followers.remove(follower)



        return Response({"message": "Unfollowed successfully!"}, status=status.HTTP_200_OK)

    return Response({"message": "You are not following this user!"}, status=status.HTTP_400_BAD_REQUEST)
