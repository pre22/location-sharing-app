import json
from django.db.models import Q
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from .models import ShareLocationRequestModel


User = get_user_model()


class LocationConsumer(WebsocketConsumer):
    async def connect(self):
        '''Websocket Handshake'''
        try:
            # Get Header 
            headers = dict(self.scope['headers'])
            # Check for token 
            token = headers.get(b'token').decode('utf-8')
            # Get User making handshake
            self.user = await self.get_user(token)
            self.share_instance = await self.get_share_request()

            self.group_name = f'{self.share_instance.peer_a.user.username}_{self.share_instance.peer_b.user.username}_location'
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

            # Check for pending notifications

            await self.accept()
        except (TokenError, InvalidToken):
            await self.close()
        except Exception as e:
            await self.close()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        data = json.loads(text_data)
        # Broadcast received location data to all connected clients
        self.send(text_data=json.dumps(data))

    @database_sync_to_async
    def get_share_request(self):
        instance = ShareLocationRequestModel.objects.get(
            Q(peer_a__user=self.user) | Q(peer_b__user=self.user)
        )
        return instance
    
    @database_sync_to_async
    def get_user(self, access_token):
        '''Accepts JWT Refresh Token and returns the user instance'''
        access_token_obj = AccessToken(access_token)
        user_id = access_token_obj['user_id'] 
        user = User.objects.get(id=user_id)
        return user