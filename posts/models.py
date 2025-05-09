from django.db import models
from django.contrib.auth.models import User
from core.base_models import BaseModel


class Post(BaseModel):
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')

    def __str__(self):
        return self.title

class Like(models.Model):
    pass