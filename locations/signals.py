from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import ShareLocationRequestModel

@receiver(post_save, sender=ShareLocationRequestModel)
def share_request_created_handler(sender, instance, created, **kwargs):
    if instance.peer_a and instance.peer_b:
       
        # Send data to websockets
        channel_layer = get_channel_layer()
        
        # Create group for the two clients
        group_name = f'{instance.peer_a.user.username}_{instance.peer_b.user.username}_location'
        async_to_sync(channel_layer.group_add)(group_name, f'peer_{instance.peer_a.user.username}')
        async_to_sync(channel_layer.group_add)(group_name, f'peer_{instance.peer_b.user.username}')
        
        # Notify clients about the created ride
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'receive',
                'message': "You can now sharing your various location",
            }
        )
