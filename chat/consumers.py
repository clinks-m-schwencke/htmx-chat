import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.template.loader import get_template
from .models import Message, Thread


class ChatConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.user = None
        self.thread = None
        self.group_name = None

    async def connect(self):
        print("ws - connect")
        # Assign websocket data
        self.thread_id = self.scope["url_route"]["kwargs"]["thread_id"]
        self.group_name = f"chat_{self.thread_id}"

        # print("####################")
        # print("thread_id", self.thread_id)
        # print("####################")

        # self.thread = Thread.objects.get(pk=self.thread_id)

        # print("####################")
        # print("thread", self.thread)
        # print("####################")

        self.user = self.scope["user"]

        print("####################")
        print("self", self)
        print("self.channel_layer", self.channel_layer)
        print("####################")

        # Join the thread websocket
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        # Accept the websocket connection
        await self.accept()

    async def disconnect(self, close_code):
        print("ws - disconnect")
        # Disconnect from websocket
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        print("ws - receive", text_data)
        # Extract data from JSON
        text_data_json = json.loads(text_data)

        print("ws - receive: JSON", text_data_json)

        # Get message
        message = text_data_json["values"]["message"]

        # Save message to db
        await self.save_message(self.thread_id, self.user, message)

        # Send chat message event to all listeners
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat_message",
                "message": message,
            },
        )

    async def chat_message(self, event):
        print("ws - chat_message", event)
        # Extract message
        message = event["message"]

        # Send message event to client
        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                }
            )
        )

    @sync_to_async
    def save_message(self, thread_id, user, message):
        print("ws - save_message", user, message)
        thread = Thread.objects.get(pk=thread_id)
        message = Message.objects.create(thread_id=thread, author=user, body=message)
        message.save()
