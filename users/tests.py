from django.urls import reverse
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from .models import CustomUser


User = get_user_model()

class AuthTests(APITestCase):

    def setUp(self):
        self.register_url = reverse('register')
        self.verify_url = reverse('verification')
        self.login_url = reverse('log-in')
        self.refresh_url = reverse('token-refresh')
        self.logout_url = reverse('auth_logout')
        self.password_reset_url = reverse('password-reset')
        self.password_confirm_url = reverse('password-confirm')

        def setUp(self):
            # Testdan oldin foydalanuvchi yaratish
            self.user_email = "reset@example.com"
            self.user_password = "Initial123!"
            self.user = CustomUser.objects.create_user(email=self.user_email, username="resetuser",
                                                       password=self.user_password)

    def test_user_registration_and_email_verification(self):
        data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "Password123",
            "password_confirm": "Password123"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Extract token from cache (simulate email verification)
        token, _ = cache.get(data["email"])
        self.assertIsNotNone(token)

        # Verify email
        response = self.client.post(self.verify_url, {"token": token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("successfully verified", response.data["detail"])

    def test_login_and_token_refresh(self):
        user = User.objects.create_user(email="test@example.com", username="testuser", password="Testpass123!")
        user.is_verified = True
        user.save()

        # Login
        response = self.client.post(self.login_url, {"email": "test@example.com", "password": "Testpass123!"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        refresh_token = response.data["refresh"]

        # Refresh token
        response = self.client.post(self.refresh_url, {"refresh": refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_password_reset_and_confirm(self):
        user = User.objects.create_user(email="reset@example.com", username="resetuser", password="Initial123!")
        user.is_verified = True
        user.save()

        # Request password reset
        response = self.client.post(self.password_reset_url, {"email": "reset@example.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        token = default_token_generator.make_token(user)

        # Confirm password reset
        data = {
            "token": token,
            "new_password": "NewStrong123!",
            "confirm_password": "NewStrong123!"
        }
        response = self.client.post(self.password_confirm_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)

    def test_logout(self):
        user = User.objects.create_user(email="logout@example.com", username="logoutuser", password="Logout123!")
        user.is_verified = True
        user.save()

        login = self.client.post(self.login_url, {"email": "logout@example.com", "password": "Logout123!"})
        refresh_token = login.data["refresh"]

        response = self.client.post(self.logout_url, {"refresh": refresh_token})
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)