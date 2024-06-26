import json
from channels.generic.websocket import AsyncWebsocketConsumer
import re
import os
import sys
import select
from django.conf import settings
from django.contrib.auth.models import User
from vibe.models import Vibrator
from asgiref.sync import sync_to_async

@sync_to_async
def get_vibrator(user):
    vibrator, created = Vibrator.objects.get_or_create(user=user)
    return vibrator

@sync_to_async
def set_vibrator(user, setting):
    vibrator, created = Vibrator.objects.get_or_create(user=user)
    if vibrator.last_set < timezone.now() - datetime.timedelta(seconds=1.0/4 - 0.07):
        vibrator.setting = setting
        vibrator.save()

@sync_to_async
def get_vibe_user(name):
    return User.objects.get(profile__name=name)

@sync_to_async
def get_user(user_id):
    print(user_id)
    return User.objects.get(id=user_id)

# Send the setting to the server from foreign user
class RemoteConsumer(AsyncWebsocketConsumer):
    vibe_user = None
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    # This function receive messages from WebSocket.
    async def receive(self, text_data):
        user = await get_user(self.scope['user'].id)
        await set_vibrator(user, text_data)
        pass
    pass

# Send the setting from the foreign user
class RemoteReceiveConsumer(AsyncWebsocketConsumer):
    vibe_user = None
    async def connect(self):
        self.vibe_user = await get_vibe_user(self.scope['url_route']['kwargs']['username'])
        await self.accept()

    async def disconnect(self, close_code):
        pass

    # This function receive messages from WebSocket.
    async def receive(self, text_data):
        print(text_data)
        vibrator = await get_vibrator(self.vibe_user)
        await self.send(text_data=vibrator.setting)
        pass
    pass
