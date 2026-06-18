# import libraries
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import Room, Message


# Create a consumer
class ChatConsumer(AsyncWebsocketConsumer):
    ## 1. connect
    async def connect(self):
        
        print(self.channel_layer)
        print(self.channel_name)
        print(self.scope)
        print(self.scope["user"])
        
        self.user = self.scope["user"].username
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.username = self.scope["url_route"]["kwargs"]["username"]
        
        self.room = await self.get_room()
        messages = await self.get_messages()
        
        print(self.user)
        print(type(self.user))
        print(messages)
        print(self.room)
        print(self.room.id)
        
        
        print("Joined Room :", self.room_name)
        print("Channel Name :", self.channel_name)
        
        print("User is connected!!!")
        
        await self.accept()

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        
        
        for msg in messages:
            await self.send(text_data = json.dumps({"type": "history", "sender": msg.sender, "message": msg.content,}))

           
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "join_message",
                "username": self.user,  #self.username
            }
        )
        
        
         
        
    
    ## Create Event Handler
    async def join_message(self, event):

        username = event["username"]

        await self.send(
            text_data=json.dumps({
                "type": "join",
                "message": f"{username} joined the room"
            })
        )
    
    ## 2. receive
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        sender = data["sender"]
        
        print("Message received :")
        print(data)
        print("Message : ", message)
        print("Sender : ", sender) 
        
        await self.save_message(sender,message)
        
        # await self.send(text_data = json.dumps({"message": message}))
        await self.channel_layer.group_send(self.room_name, {"type": "chat_message", "message": message, "sender": sender,})
        
    
    ## Create Event Handler
    async def chat_message(self, event):
        message = event["message"]
        sender = event["sender"]
        
        await self.send(text_data = json.dumps({"message": message, "sender": sender}))
    
    
    ## 3. disconnect
    async def disconnect(self, code):
        await self.channel_layer.group_send(
        self.room_name,
        {
            "type": "leave_message",
            "username": self.username,
        }
    )
        
        
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
        print("User Disconnected")
        
    ## Create Event Handler        
    async def leave_message(self, event):

        username = event["username"]

        await self.send(
            text_data=json.dumps({
                "type": "leave",
                "message": f"{username} left the room"
            })
        )
        
        
    ## Create Database Helper

    @database_sync_to_async
    def get_room(self):
        room, created = Room.objects.get_or_create(name = self.room_name)
            
        return room
    
    @database_sync_to_async
    def save_message(self, sender, message):
        return Message.objects.create(room = self.room, sender = sender, content = message) 
    
    @database_sync_to_async
    def get_messages(self):
        return list(self.room.messages.all().order_by("created_at"))