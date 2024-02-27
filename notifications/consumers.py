import json
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from jwt.exceptions import InvalidTokenError
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

User = get_user_model()

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


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            # Get Header 
            headers = dict(self.scope['headers'])
            # Check for token 
            token = headers.get(b'token').decode('utf-8')
            # Get User making handshake
            self.user = await self.get_user(token)

            self.group_name = f'{self.user.id}_notificaton'
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

            await self.accept()
        except (TokenError, InvalidToken):
            await self.close()
        except Exception as e:
            await self.close()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        print('Here', self.user.email, event['recipient'])
        if self.user.email == event['recipient']:
            await self.send(text_data=json.dumps({ 'message': event['message'] }))

    @database_sync_to_async
    def get_user(self, access_token):
        access_token_obj = AccessToken(access_token)
        user_id = access_token_obj['user_id'] 
        user = User.objects.get(id=user_id)
        return user