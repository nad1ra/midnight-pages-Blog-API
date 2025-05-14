from rest_framework.test import APITestCase
from rest_framework import status
from users.models import CustomUser
from posts.models import Post, Like
from django.contrib.auth.models import User


class PostTests(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", password="password123")
        self.client.login(username="testuser", password="password123")

        self.post_data = {
            "title": "Test Post",
            "content": "This is a test post.",
        }
        self.post = Post.objects.create(title="Test Post", content="Test Content", author=self.user)

    def test_create_post(self):
        url = '/api/posts/'
        response = self.client.post(url, self.post_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(response.data['title'], "Test Post")

    def test_get_post(self):
        url = f'/api/posts/{self.post.id}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.post.title)
        self.assertEqual(response.data['content'], self.post.content)

    def test_update_post(self):
        url = f'/api/posts/{self.post.id}/'
        updated_data = {
            "title": "Updated Post",
            "content": "Updated Content",
        }
        response = self.client.put(url, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Updated Post")
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated Post")

    def test_delete_post(self):
        url = f'/api/posts/{self.post.id}/'
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 0)

    def test_like_post(self):
        url = f'/api/posts/{self.post.id}/like/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["detail"], "Post liked successfully.")
        self.assertEqual(Like.objects.count(), 1)

    def test_unlike_post(self):
        url_like = f'/api/posts/{self.post.id}/like/'
        self.client.post(url_like)

        url_unlike = f'/api/posts/{self.post.id}/unlike/'
        response = self.client.post(url_unlike)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data["detail"], "Post unliked successfully.")
        self.assertEqual(Like.objects.count(), 0)

    def test_like_post_already_liked(self):
        url_like = f'/api/posts/{self.post.id}/like/'
        self.client.post(url_like)

        response = self.client.post(url_like)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "You already liked this post.")

    def test_unlike_post_not_liked(self):
        url_unlike = f'/api/posts/{self.post.id}/unlike/'
        response = self.client.post(url_unlike)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "You have not liked this post yet.")