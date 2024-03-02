import json
from django.db.models import Q
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from .models import ShareLocationRequestModel


User = get_user_model()


class LocationConsumer(AsyncWebsocketConsumer):
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

            if self.share_instance == None:
                await self.close()
                    
            self.group_name = f'{self.share_instance.peer_a.user.username}_{self.share_instance.peer_b.user.username}_location'

            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

            await self.accept()
        except (TokenError, InvalidToken):
            await self.close()
        except Exception as e:
            await self.close()

    async def disconnect(self, close_code):
        '''Discard Group and Channel when Client disconnects'''
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        data = json.loads(text_data)

        await self.broadcast_message(data)


    async def broadcast_message(self, data):
        
        await self.channel_layer.group_send(
            self.group_name,  
            {
                "type": "send_message",
                "data": data,
            }
        )


    async def send_message(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    @database_sync_to_async
    def get_share_request(self):
        try:
            instance = ShareLocationRequestModel.objects.select_related('peer_a__user', 'peer_b__user').get(
                Q(peer_a__user=self.user) | Q(peer_b__user=self.user)
            )
            

            if instance.peer_a and instance.peer_a:
                return instance
            
            elif instance.peer_a == "" or instance.peer_b == "":
                return None
        except ShareLocationRequestModel.DoesNotExist:
            return None
    
    @database_sync_to_async
    def get_user(self, access_token):
        '''Accepts JWT Refresh Token and returns the user instance'''
        access_token_obj = AccessToken(access_token)
        user_id = access_token_obj['user_id'] 
        user = User.objects.get(id=user_id)
        return user