from rest_framework import serializers
from rest_framework.exceptions import NotFound
from .models import CustomUser, UserProfile


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Password and confirm password do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = instance.id
        representation['email'] = instance.email
        representation['username'] = instance.username
        representation['is_active'] = instance.is_active
        representation['is_verified'] = instance.is_verified
        representation['date_joined'] = instance.date_joined.isoformat()
        representation['role'] = instance.role
        return representation


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        if not value:
            raise serializers.ValidationError("Token is required.")
        return value


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'email',
            'username',
            'is_active',
            'is_staff',
            'is_verified',
            'date_joined',
            'role'
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio', 'image', 'followers_count', 'following_count']

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()

    def to_representation(self, instance):
        username = self.context.get('username', None)
        if username:
            user_profile = UserProfile.objects.filter(user__username=username).first()
            if not user_profile:
                raise NotFound(detail="Profile is not found")
            return super().to_representation(user_profile)
        return super().to_representation(instance)