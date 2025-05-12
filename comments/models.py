from django.db import models
from core.base_models import BaseModel
from users.models import CustomUser
from posts.models import Post


class Comment(BaseModel):
    content = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return f'{self.author} commented {self.post}'