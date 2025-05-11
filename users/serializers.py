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

        if len(data['password']) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in data['password']):
            raise serializers.ValidationError("Password must contain at least one number.")
        if not any(char.isalpha() for char in data['password']):
            raise serializers.ValidationError("Password must contain at least one letter.")
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
        representation['date_joined'] = instance.date_joined.isoformat() if instance.date_joined else None
        representation['role'] = instance.role
        return representation


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        if not value:
            raise serializers.ValidationError("Token is required.")
        return value


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = CustomUser.objects.get(email=value)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address.")
        return user


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField(min_length=8)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("The password and confirmation password do not match.")

        if len(attrs['new_password']) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")

        if not any(char.isdigit() for char in attrs['new_password']):
            raise serializers.ValidationError("Password must contain at least one number.")

        if not any(char.isalpha() for char in attrs['new_password']):
            raise serializers.ValidationError("Password must contain at least one letter.")

        return attrs


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

        if username is not None:  # Ensure username exists in context
            user_profile = UserProfile.objects.filter(user__username=username).first()
            if not user_profile:
                raise NotFound(detail="Profile not found for the given username.")
            return super().to_representation(user_profile)

        return super().to_representation(instance)


