from django.test import TestCase
from django.urls import reverse
from channels.routing import URLRouter, get_default_application
from channels.testing import WebsocketCommunicator
from .consumers import NotificationConsumer
from .models import Notification
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
import json

User = get_user_model()


class NotificationConsumerTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        cls.access_token = AccessToken.for_user(cls.test_user)
        cls.test_notification = Notification.objects.create(user=cls.test_user, message='Test message', delivered=False)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.test_user.delete()

    async def connect_to_consumer(self, access_token):
        communicator = WebsocketCommunicator(NotificationConsumer, '/ws/notify/')
        communicator.scope['headers'] = [(b'token', access_token)]
        return communicator
    
    async def test_connect_with_valid_token(self):
        communicator = await self.connect_to_consumer(self.access_token)
        connected, _ = await communicator.connect(timeout=60)
        self.assertTrue(connected)
        await communicator.disconnect()

    # async def test_connect_with_invalid_token(self):
    #     communicator = await self.connect_to_consumer('invalid_token')
    #     connected, _ = await communicator.connect()
    #     self.assertFalse(connected)

    # async def test_send_notification(self):
    #     communicator = await self.connect_to_consumer(self.access_token)
    #     await communicator.connect()
    #     message = {
    #         'id': self.test_notification.id,
    #         'message': self.test_notification.message,
    #         'recipient': self.test_notification.user
    #     }
    #     await communicator.send_json_to(message)
    #     await communicator.disconnect()

    # async def test_receive_notification(self):
    #     communicator = await self.connect_to_consumer(self.access_token)
    #     response = await communicator.receive_json_from()
    #     response_data = json.loads(response)
    #     self.assertEqual(response_data['message'], self.test_notification.message)
    #     await communicator.disconnect()

    # async def test_send_pending_notifications(self, mock_sync_to_async):
    #     # Create pending notifications
    #     Notification.objects.create(user=User.objects.create(email="test@example.com"), message="Pending 1", delivered=False)
    #     Notification.objects.create(user=User.objects.create(email="test2@example.com"), message="Pending 2", delivered=False)

    #     communicator = await self.connect_to_consumer(self.access_token)
    #     await communicator.connect()

    #     # Assert both pending notifications are received
    #     response1 = await communicator.receive_json_from()
    #     response2 = await communicator.receive_json_from()
    #     self.assertEqual(response1['message'], "Pending 1")
    #     self.assertEqual(response2['message'], "Pending 2")

    #     await communicator.disconnect()

    # async def test_mark_notification_as_delivered(self, mock_sync_to_async):
    #     notification = Notification.objects.create(user=User.objects.create(email="test@example.com"), message="Test", delivered=False)
    #     communicator = await self.connect_to_consumer(self.access_token)
    #     await communicator.send_json_to({
    #         'id': notification.id,
    #         'message': notification.message,
    #         'recipient': notification.user.email
    #     })
    #     await communicator.disconnect()
    #     notification.refresh_from_db()
    #     self.assertTrue(notification.delivered)