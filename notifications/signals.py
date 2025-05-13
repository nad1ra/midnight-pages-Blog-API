from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from posts.models import Post
from comments.models import Comment
from users.models import Follow
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=Post)
def notify_on_like(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        liker = instance.user
        owner = post.author
        if liker != owner:
            Notification.objects.create(
                user=owner,
                verb=f"{liker.username} liked your post.",
                is_read=False
            )

@receiver(post_save, sender=Comment)
def notify_on_comment(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        commenter = instance.user
        owner = post.author
        if commenter != owner:
            Notification.objects.create(
                user=owner,
                verb=f"{commenter.username} commented on your post.",
                is_read=False
            )

@receiver(post_save, sender=Follow)
def notify_on_follow(sender, instance, created, **kwargs):
    if created:
        follower = instance.follower
        following = instance.following
        if follower != following:
            Notification.objects.create(
                user=following,
                verb=f"{follower.username}  started following you.",
                is_read=False
            )
