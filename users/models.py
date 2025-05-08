from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    role = models.CharField(
        max_length=20,
        choices=[
            ('user', 'User'),
            ('admin', 'Admin'),
            ('moderator', 'Moderator'),
        ],
        default='user'
    )

    REQUIRED_FIELDS = ['email']
    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profiles')
    bio = models.TextField(max_length=200)
    image = models.ImageField()
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)

    @property
    def followers_count(self):
        return self.followers.count()

    @property
    def following_count(self):
        return self.following.count()


