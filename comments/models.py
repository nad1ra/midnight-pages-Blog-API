from django.db import models
from core.base_models import BaseModel
from users.models import CustomUser
from posts.models import Post


class Comment(BaseModel):
    content = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')  # Fixed: Removed default=1
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')  # Fixed: Direct reference to Post

    def __str__(self):  # Fixed: Added double underscores
        return f'{self.author} commented on {self.post}'