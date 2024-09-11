import json, threading
from channels.generic.websocket import AsyncWebsocketConsumer
import re
import os
import sys
import select
from django.conf import settings
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from .models import Camera
import pytz, datetime
from django.utils import timezone
from django.conf import settings
import base64
import urllib.parse

@sync_to_async
def get_camera_status(camera_user, camera_name):
    return Camera.objects.get_or_create(name=camera_name, user__profile__name=camera_user).data

@sync_to_async
def update_camera(camera_user, camera_name, camera_data):
    camera, created = Camera.objects.get_or_create(name=camera_name, user__profile__name=camera_user)
    camera.connected = timezone.now()
    camera.data = camera_data
    camera.save()

@sync_to_async
def get_user(id):
    user = User.objects.get(id=int(id))
#    if not (user.profile.vendor or user.is_superuser): return False
    return True

@sync_to_async
def get_auth(user_id, session_key):
    from security.tests import face_mrz_or_nfc_verified_session_key
    user = User.objects.get(id=int(user_id)) if user_id else None
    return face_mrz_or_nfc_verified_session_key(user, session_key)

class PhotoboothConsumer(AsyncWebsocketConsumer):
    camera_user = None
    camera_name = None
    async def connect(self):
        self.camera_user = self.scope['url_route']['kwargs']['username']
        self.camera_name = self.scope['url_route']['kwargs']['name']
        auth = await get_user(self.scope['user'].id)
        auth2 = await get_auth(self.scope['user'].id, self.scope['session'].session_key)
        if not (auth and auth2): return
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text = await update_camera(self.camera_user, self.camera_name, text_data)
        await self.send(text_data=text)

    pass

class PhotoboothRemoteConsumer(AsyncWebsocketConsumer):
    camera_user = None
    camera_name = None
    async def connect(self):
        self.camera_user = self.scope['url_route']['kwargs']['username']
        self.camera_name = self.scope['url_route']['kwargs']['name']
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        if not text_data == 'i':
            text = await update_camera(self.camera_user, self.camera_name, text_data)
        text = await get_camera_status(self.camera_user, self.camera_name)
        await self.send(text_data=text)

    pass
