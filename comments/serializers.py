from rest_framework import serializers
from .models import Comment
from posts.serializers import PostSerializer
from posts.models import Post
from users.serializers import CustomUserSerializer


class CommentSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())
    # likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'content', 'author', 'post', 'created_at', 'updated_at', 'is_active')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def create(self, validated_data):
        user = self.context['request'].user
        return Comment.objects.create(user=user, **validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['post'] = PostSerializer(instance.post).data
        return rep