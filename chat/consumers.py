import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import render
from django.template.loader import get_template
from django.utils.translation import gettext as _
from .models import Message, Thread

## TODO: Rewrite to handle different kinds of interations in single consumer
## Thread resolve
## Thread unresolve
## Thread request resolve
## Thread request unresolve ??
## Thread deleted
## Thread undeleted
## Message edited
## Message deleted


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.user = None
        self.thread = None
        self.group_name = None

    async def connect(self):
        print("####################")
        print("ws - connect")
        print("####################")
        # Assign websocket data
        self.thread_id = self.scope["url_route"]["kwargs"]["thread_id"]
        self.group_name = f"chat_{self.thread_id}"

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
        print("####################")
        print("ws - disconnect")
        print("####################")
        # Disconnect from websocket
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        print("####################")
        print("ws - receive", text_data)
        print("####################")
        # Extract data from JSON
        text_data_json = json.loads(text_data)

        # Get Data
        data = text_data_json["values"]

        # Get Action
        action = data["action"]

        print("action", action)

        match action:
            case "message-new":
                await self.handle_chat_message_new(data)
            case "message-edit":
                pass
            case "message-delete":
                pass
            case "thread-resolve":
                await self.handle_thread_resolve(data)
            case "thread-unresolve":
                pass
            case "thread-request-resolve":
                pass
            case "thread-request-unresolve":
                pass
            case "thread-edit":
                pass
            case "thread-delete":
                pass
            case "thread-undelete":
                pass
            case _:
                print(f"Unhandled websocket event '{action}'")

    ###################
    # Action Handlers #
    ###################

    async def handle_chat_message_new(self, data):
        print("####################")
        print("ws:handler - handle_chat_message_new", data)
        print("####################")
        # Get message
        message = data["message"]

        # Save message to db
        await self.create_message(self.thread_id, self.user, message)

        # Send chat message event to all listeners
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message.new",
                "message": message,
                "username": self.user.username,
                "target": "#message-list",
                "swap": "append",
            },
        )

    async def handle_thread_resolve(self, data):
        print("####################")
        print("ws:handler - handle_thread_resolve", data)
        print("####################")

        message = _("%(user)s has resolved the thread.") % {"user": self.user.username}
        await self.create_message(self.thread_id, self.user, message)

        await self.set_resolved(self.thread_id, True)

        # Send thread resolved
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "thread.resolved",
                "is_resolved": True,
            },
        )
        # Send chat message event to all listeners
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message.new",
                "message": message,
                "username": self.user.username,
                "target": "#message-list",
                "swap": "append",
            },
        )

    async def handle_thread_edit(self, data):
        print("####################")
        print("ws:handler - handle_thread_edit", data)
        print("####################")

    ####################
    # Database Methods #
    ####################

    @sync_to_async
    def create_message(self, thread_id, user, message):
        print("####################")
        print("ws:db - save_message", user, message)
        print("####################")
        thread = Thread.objects.get(pk=thread_id)
        message = Message.objects.create(thread_id=thread, author=user, body=message)
        message.save()

    @sync_to_async
    def set_resolved(self, thread_id, is_resolved):
        print("####################")
        print("ws:db - set_resolved", thread_id, is_resolved)
        print("####################")
        thread = Thread.objects.get(pk=thread_id)
        thread.is_resolved = is_resolved
        thread.save()

    ############################
    # Websocket Event handlers #
    ############################

    async def chat_message_new(self, event):
        print("####################")
        print("ws:event - chat_message", event)
        print("####################")

        # Extract message
        message = event["message"]
        username = event["username"]
        target = event.get("target")
        swap = event.get("swap")

        # Send message event to client
        payload = get_template("chat/thread_detail.html#message_display").render(
            context={"message": {"author": username, "body": message}}
        )

        data = {"payload": payload}

        if target:
            data["target"] = target
        if swap:
            data["swap"] = swap

        print("####################")
        print("ws - chat_message payload", payload)

        response = json.dumps(data)
        print("####################")
        print("ws - chat_message response", response)

        await self.send(text_data=response)

    async def thread_resolved(self, event):
        """
        Web socket event for resolving or unresolving a thread
        """

        print("####################")
        print("ws:event - thread_resolved", event)
        print("####################")
        is_resolved = event["is_resolved"]
        template = (
            "chat/thread_detail.html#resolved-thread-button"
            if is_resolved
            else "chat/thread_detail.html#unresolved-thread-button"
        )
        payload = get_template(template).render()
        response = json.dumps({"payload": payload})
        await self.send(text_data=response)

    async def thread_edited(self, event):
        """
        Websocket event for editing a thread's title / body
        """
        print("####################")
        print("ws:event - thread_edited", event)
        print("####################")
        payload = get_template("chat/thread_detail#thread-title").render()
        data = {
            "payload": payload,
            "target": "#thread-title",
            "swap": "outerHTML",
        }
        response = json.dumps(data)
        await self.send(text_data=response)
