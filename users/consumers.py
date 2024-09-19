# messaging/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['username']
        self.room_group_name = f'chat_{self.room_name}'
        
        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender = self.scope['user']
        recipient_username = data['recipient']

        # Fetch recipient user asynchronously
        recipient_user = await sync_to_async(User.objects.get)(username=recipient_username)
        
        # Save message in the database asynchronously
        new_message = await sync_to_async(Message.objects.create)(
            sender=sender, recipient=recipient_user, content=message
        )

        # Send message to the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender.username,
                'recipient': recipient_username,
                'timestamp': str(new_message.timestamp)
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        recipient = event['recipient']
        timestamp = event['timestamp']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'recipient': recipient,
            'timestamp': timestamp
        }))

# messaging/consumers.py

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = f'notifications_{self.scope["user"].username}'
        
        # Join the notification group for the user
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the notification group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):
        # Send notification to WebSocket
        await self.send(text_data=json.dumps(event['notification']))

    # Method to call when sending a notification
    @classmethod
    async def send_user_notification(cls, recipient, sender):
        await cls.channel_layer.group_send(
            f'notifications_{recipient.username}',
            {
                'type': 'send_notification',
                'notification': {
                    'message': f'{sender.username} sent you a message',
                }
            }
        )
