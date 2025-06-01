from django.core.cache import cache
from rest_framework import serializers
from .models import CustomUser, UserProfile
from .services import send_verification_token
from .exceptions import TokenExpiredOrInvalid


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id','email', 'username', 'password', 'password_confirm']

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
        token = CustomUser.generate_token()

        # Create a user instance but do not save it yet
        user = CustomUser(
            email=validated_data["email"],
            username=validated_data["username"]
        )
        user.set_password(validated_data["password"])
        user.is_active = False
        user.is_verified = False

        # Cache user data for email verification
        user_data = {
            "email": user.email,
            "username": user.username,
            "password": validated_data["password"],  # required for final creation
        }

        cache.set(user.email, (token, user_data), timeout=300)
        cache.set(token, user.email, timeout=300)
        send_verification_token(user.email, token)

        # Return an *unsaved* user instance for serialization
        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = instance.id
        representation['email'] = instance.email
        representation['username'] = instance.username
        representation['is_active'] = instance.is_active
        representation['is_staff'] = instance.is_staff
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

    def save(self, **kwargs):
        token = self.validated_data.get("token")
        email = cache.get(token)
        if not email:
            raise TokenExpiredOrInvalid
        cached = cache.get(email)
        if not cached:
            raise TokenExpiredOrInvalid
        cached_token, user_data = cached
        if cached_token != token:
            raise TokenExpiredOrInvalid

        user = CustomUser.objects.create_user(**user_data)
        user.is_verified = True
        user.is_active = True
        user.save()

        cache.delete(email)
        cache.delete(token)
        return user


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not CustomUser.objects.filter(email__iexact=value, is_active=True).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(min_length=8)
    password_confirm = serializers.CharField(min_length=8)

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("The password and confirmation password do not match.")

        if len(attrs['password']) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")

        if not any(char.isdigit() for char in attrs['password']):
            raise serializers.ValidationError("Password must contain at least one number.")

        if not any(char.isalpha() for char in attrs['password']):
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


class ProfileByUsernameSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio', 'image', 'followers_count', 'following_count']

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()


class UserProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user',
            'bio',
            'image',
            'followers_count',
            'following_count'
        ]
        read_only_fields = [
            'id',
            'user'
            'followers_count',
            'following_count'
        ]

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()
