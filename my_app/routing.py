from django.urls import re_path
from my_app import consumers

websocket_urlpatterns = [
    re_path(r'ws/audio/', consumers.AudioConsumer.as_asgi()),
]
