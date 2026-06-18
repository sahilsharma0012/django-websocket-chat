from django.urls import path, re_path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    re_path("ws/chat/(?P<room_name>\w+)/(?P<username>\w+)/$", ChatConsumer.as_asgi(),),
]