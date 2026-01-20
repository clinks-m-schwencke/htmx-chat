from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/chat/<int:thread_id>", consumers.ChatConsumer.as_asgi()),
    path("ws/thread/<int:thread_id>", consumers.ChatConsumer.as_asgi()),
]
