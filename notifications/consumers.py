import json
import traceback
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from jwt.exceptions import InvalidTokenError
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from .models import Notification

User = get_user_model()


# Preferrable for MVT, MVC Web applications 
class NotificationConsumers(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'public_room'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({ 'message': event['message'] }))


# Preferrable for Clients such as mobile app, frontend frameworks 
class NotificationConsumer(AsyncWebsocketConsumer):
    '''
    Sends Notifications to connected Clients.
    Similar to a regular django view but for websocket
    '''
    async def connect(self):
        '''Websocket Handshake'''
        try:
            # Get Header 
            headers = dict(self.scope['headers'])
            # Check for token 
            token = headers.get(b'token')
            # Get User making handshake
            self.user = await self.get_user(token)

            self.group_name = f'{self.user.id}_notificaton'
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

            # Check for pending notifications

            await self.accept()
            await self.send_pending_notifications()
        except (TokenError, InvalidToken):
            await self.close()
        except Exception as e:
            await self.close()

    async def disconnect(self, code):
        '''Discard Group and Channel when Client disconnects'''
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def send_notification(self, event):
        '''Sends the Nofitications to the Client'''

        if self.user.email == event['recipient']:
            await self.send(text_data=json.dumps({ 'message': event['message'] }))
            await self.mark_notification_as_delivered(event['id'])

    async def send_pending_notifications(self):
        '''Send Pending Notification(Notifications with delivered status == False)'''
        pending_notifications = await self.get_pending_notifications()

        for notification_data in pending_notifications:

            await self.send_notification(
                {
                    "id": notification_data['id'],
                    "message": notification_data['message'],
                    "recipient": notification_data['user__email']
                }
            )

    @database_sync_to_async
    def get_pending_notifications(self):
        '''Return a list of Notification Instances where delivered status == False'''
        pending_list = list(Notification.objects.filter(user=self.user, delivered=False).values('id', 'message', 'user__email'))
        return pending_list
    
    
    @database_sync_to_async
    def mark_notification_as_delivered(self, notification_id):
        '''Updates the delivered status of a Notification Instance True'''
       
        instance = Notification.objects.get(id=notification_id)
        instance.delivered = True
        instance.save()
        return instance
        

    @database_sync_to_async
    def get_user(self, access_token):
        '''Accepts JWT Refresh Token and returns the user instance'''
        access_token_obj = AccessToken(access_token)
        user_id = access_token_obj['user_id']
        user = User.objects.get(id=user_id)
        return user
    



    