from rest_framework.test import APITestCase
from rest_framework import status
from users.models import CustomUser
from posts.models import Post, Like
from comments.models import Comment


class CommentTests(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", password="password123")
        self.client.login(username="testuser", password="password123")

        self.post = Post.objects.create(title="Test Post", content="Test Content", author=self.user)

        self.comment_data = {
            "content": "Test Comment",
            "post": self.post.id,
        }

    def test_create_comment(self):
        url = '/api/comments/'
        response = self.client.post(url, self.comment_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(response.data['content'], "Test Comment")

    def test_get_comment(self):
        comment = Comment.objects.create(content="Test Comment", post=self.post, author=self.user)

        url = f'/api/comments/{comment.id}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], comment.content)
        self.assertEqual(response.data['post'], self.post.id)

    def test_update_comment(self):
        comment = Comment.objects.create(content="Test Comment", post=self.post, author=self.user)

        url = f'/api/comments/{comment.id}/'
        updated_data = {
            "content": "Updated Comment Content",
            "post": self.post.id,
        }
        response = self.client.put(url, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], "Updated Comment Content")
        comment.refresh_from_db()
        self.assertEqual(comment.content, "Updated Comment Content")

    def test_delete_comment(self):
        comment = Comment.objects.create(content="Test Comment", post=self.post, author=self.user)

        url = f'/api/comments/{comment.id}/'
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

    def test_like_comment(self):
        url = f'/api/comments/{self.comment.id}/like/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["detail"], "Comment liked successfully.")
        self.assertEqual(Like.objects.count(), 1)

    def test_unlike_comment(self):
        url_like = f'/api/comments/{self.comment.id}/like/'
        self.client.post(url_like)

        url_unlike = f'/api/comments/{self.comment.id}/unlike/'
        response = self.client.post(url_unlike)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data["detail"], "Comment unliked successfully.")
        self.assertEqual(Like.objects.count(), 0)

    def test_like_comment_already_liked(self):
        url_like = f'/api/comments/{self.comment.id}/like/'
        self.client.post(url_like)

        response = self.client.post(url_like)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "You already liked this comment.")

    def test_unlike_comment_not_liked(self):
        url_unlike = f'/api/comments/{self.comment.id}/unlike/'
        response = self.client.post(url_unlike)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "You have not liked this comment yet.")
