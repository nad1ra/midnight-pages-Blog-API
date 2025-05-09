from rest_framework import serializers
# from users.serializers import UserSerializer
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    # author = UserSerializer(read_only=True)
    # likes_count = serializers.SerializerMethodField()
    # comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'author', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def create(self, validated_data):
        user = self.context['request'].user
        return Post.objects.create(user=user, **validated_data)