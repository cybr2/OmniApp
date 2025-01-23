import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import Message
from asgiref.sync import sync_to_async
from django.utils import timezone
import base64
import uuid 
from django.core.files.base import ContentFile
from django.conf import settings


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        user1 = self.scope['user'].username 
        user2 = self.room_name
        self.room_group_name = f"chat_{''.join(sorted([user1, user2]))}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Fetch chat history and send to the client
        chat_history = await self.get_chat_history(user1, user2)
        await self.send(text_data=json.dumps({
            'type': 'chat_history',
            'messages': chat_history
        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '').strip()
        sender = self.scope['user']
        receiver = await self.get_receiver_user()

        file_data = data.get('file')

        # If there's a file, process it
        if file_data:
            file_name = file_data.get('name', f'{uuid.uuid4()}')
            file_content = base64.b64decode(file_data['content'].split(',')[1])
            file_obj = ContentFile(file_content, name=file_name)
            message_instance = await self.save_message(sender, receiver, message, file_obj)
        elif message:  # If there's no file, but there's a message
            message_instance = await self.save_message(sender, receiver, message)
        else:
            # If neither message nor file is provided, we just return (no action)
            return
        timestamp = timezone.localtime(message_instance.timestamp).strftime("%b. %d, %Y, %I:%M %p")

        broadcast_data = {
            'type': 'chat_message',
            'sender': sender.username,
            'receiver': receiver.username,
            'message': message,
            'timestamp': timestamp
        }

        if file_data:
            file_url = message_instance.file.url
            if file_url.startswith(settings.MEDIA_URL):
                file_url = file_url[len(settings.MEDIA_URL):]
            full_file_url = f"{settings.MEDIA_URL}{file_url}"  # Ensure the full URL
            print(f"File URL: {full_file_url}") # Debugging print
            broadcast_data['file'] = {
                'name': file_name,
                'url': full_file_url if message_instance.file else None
            }


        # Broadcast message to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            broadcast_data
        )
    
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        receiver = event['receiver']
        timestamp = event['timestamp']

        file_data = event.get('file')

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'sender': sender,
            'receiver': receiver,
            'message': message,
            'timestamp': timestamp,
            'file': file_data
        }))
    
    @sync_to_async
    def save_message(self, sender, receiver, message, file=None):
        return Message.objects.create(sender=sender, receiver=receiver, content=message, file=file)

    @sync_to_async
    def get_receiver_user(self):
        return User.objects.get(username=self.room_name)
    
    @sync_to_async
    def get_chat_history(self, user1, user2):
        # Fetch the user objects based on the provided usernames
        user1 = User.objects.get(username=user1)
        user2 = User.objects.get(username=user2)
        # Fetch messages where sender or receiver is either user1 or user2
        messages = Message.objects.filter(
            sender__in=[user1.id, user2.id],  # Use the user ids, not the objects themselves
            receiver__in=[user1.id, user2.id]  # Use the user ids, not the objects themselves
        ).order_by('timestamp')

        # Format messages for sending
        return [
        {
            'sender': message.sender.username,
            'receiver': message.receiver.username,
            'message': message.content,
            'file': {
                'name': message.file.name.split('/')[-1] if message.file else None,
                'url': message.file.url if message.file else None
            } if hasattr(message, 'file') else None,
            'timestamp': timezone.localtime(message.timestamp).strftime("%b. %d, %Y, %I:%M %p")
        }
        for message in messages
    ]
