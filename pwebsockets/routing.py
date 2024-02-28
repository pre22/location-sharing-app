from django.urls import re_path
from notifications.consumers import NotificationConsumer
from locations.consumer import LocationConsumer


websocket_urlpatterns = [
    re_path(r"ws/notify/", NotificationConsumer.as_asgi()),
    re_path(r"ws/location/", LocationConsumer.as_asgi()),
]