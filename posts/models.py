from django.db import models
from users.models import CustomUser
from core.base_models import BaseModel


class Post(BaseModel):
    title = models.CharField(max_length=100)
    content = models.TextField(default="No content")
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posts')

    def __str__(self):  # Fixed: Added double underscores
        return self.title


class Like(BaseModel):  # Fixed: Now inherits from BaseModel
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='likes')  # Fixed: Changed to ForeignKey and plural related_name
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes', null=True, blank=True)  # Fixed: Direct reference to Post, made nullable
    comment = models.ForeignKey('comments.Comment', on_delete=models.CASCADE, related_name='likes', null=True, blank=True)  # Fixed: Made nullable

    class Meta:
        unique_together = ('user', 'post', 'comment')
        constraints = [
            models.CheckConstraint(
                check=models.Q(post__isnull=False) | models.Q(comment__isnull=False),
                name='like_has_post_or_comment'
            ),
            models.CheckConstraint(
                check=~(models.Q(post__isnull=False) & models.Q(comment__isnull=False)),
                name='like_not_both_post_and_comment'
            )
        ]

    def __str__(self):  # Fixed: Added double underscores
        if self.post:
            return f"{self.user} liked post: {self.post}"
        return f"{self.user} liked comment: {self.comment}"