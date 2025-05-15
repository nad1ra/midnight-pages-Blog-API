from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from notifications.models import Notification

User = get_user_model()

class NotificationAPITestCase(APITestCase):
    def setUp(self):

        self.user = User.objects.create_user(username='testuser', password='pass1234')
        self.other_user = User.objects.create_user(username='otheruser', password='pass1234')

        self.client.login(username='testuser', password='pass1234')

        self.notification = Notification.objects.create(
            user=self.user,
            verb='You got a new message',
            is_read=False
        )

        self.list_url = reverse('notification-list')
        self.detail_url = reverse('notification-detail', kwargs={'pk': self.notification.pk})
        self.mark_as_read_url = reverse('notification-mark-as-read', kwargs={'pk': self.notification.pk})

    def test_list_notifications(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['verb'], 'You got a new message')

    def test_create_notification(self):
        data = {'verb': 'Test notification'}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Notification.objects.filter(verb='Test notification').exists())

    def test_retrieve_notification(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['verb'], 'You got a new message')

    def test_update_notification(self):
        data = {'verb': 'Updated notification', 'is_read': True}
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, 200)
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.verb, 'Updated notification')
        self.assertTrue(self.notification.is_read)

    def test_delete_notification(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Notification.objects.filter(pk=self.notification.pk).exists())

    def test_mark_notification_as_read(self):
        response = self.client.put(self.mark_as_read_url)
        self.assertEqual(response.status_code, 200)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

    def test_permission_denied_for_other_user(self):
        self.client.logout()
        self.client.login(username='otheruser', password='pass1234')
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 403)
