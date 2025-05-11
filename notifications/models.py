from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    verb = models.CharField(max_length=300)
    is_read = models.BooleanField(default=True)
    time = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-time']

    def __str__(self):
        return f"{self.user.username} - {self.verb}"