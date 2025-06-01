from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework import permissions
from .models import Notification
from .serializers import NotificationSerializer
from core.permissions import IsOwner
from rest_framework.views import APIView



class NotificationListView(generics.ListCreateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        print("Request user:", self.request.user)
        return Notification.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class NotificationMarkAsReadView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def post(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response({"detail": "Notification not found."}, status=status.HTTP_404_NOT_FOUND)

        notification.is_read = True
        notification.save()

        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)