import json
from channels.generic.websocket import WebsocketConsumer

class LocationConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        data = json.loads(text_data)
        # Broadcast received location data to all connected clients
        self.send(text_data=json.dumps(data))