from django.db import models
from core.base_models import BaseModel
from django.contrib.auth.models import User


class Comment(BaseModel):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return f'{self.author} commented {self.post}'