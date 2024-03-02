# location_sharing/tests.py
from channels.testing import WebsocketCommunicator
from .consumer import LocationConsumer
from channels.routing import URLRouter
from django.test import TestCase
from pwebsockets.routing import websocket_urlpatterns

class WebSocketTestCase(TestCase):
    async def test_location_sharing(self):
        communicator1 = WebsocketCommunicator(LocationConsumer, '/ws/location/')
        communicator2 = WebsocketCommunicator(LocationConsumer, '/ws/location/')

        connected1, _ = await communicator1.connect()
        connected2, _ = await communicator2.connect()

        assert connected1
        assert connected2

        # Send location data from user 1
        location_data1 = {'user_id': 1, 'latitude': 40.7128, 'longitude': -74.0060}
        await communicator1.send_json_to(location_data1)
        response1 = await communicator1.receive_json_from()

        # Send location data from user 2
        location_data2 = {'user_id': 2, 'latitude': 34.0522, 'longitude': -118.2437}
        await communicator2.send_json_to(location_data2)
        response2 = await communicator2.receive_json_from()

        # Check if both clients received the correct location data
        assert response1 == location_data1
        assert response2 == location_data2

        # Close connections
        await communicator1.disconnect()
        await communicator2.disconnect()
