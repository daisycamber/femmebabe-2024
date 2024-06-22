import json
from channels.generic.websocket import AsyncWebsocketConsumer
import re
import os
import sys
import select
import paramiko
import time
from django.conf import settings
import threading
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
import asyncio
from .tests import face_mrz_or_nfc_verified

@sync_to_async
def get_user(id):
    user = User.objects.get(id=int(id))
    if not (user.profile.admin or user.is_superuser): return False
    return True

@sync_to_async
def get_auth(user_id, session_key):
    from security.tests import face_mrz_or_nfc_verified_session_key
    user = User.objects.get(id=int(user_id)) if user_id else None
    return face_mrz_or_nfc_verified_session_key(user, session_key) != False

@sync_to_async
def reset_session(user_id):
    user = User.objects.get(id=int(user_id))
    if user:
        for scan in user.mrz_scans.filter(valid=True, timestamp__gte=timezone.now()-datetime.timedelta(minutes=settings.MRZ_SCAN_REQUIRED_MINUTES)):
            scan.valid = False
            scan.save()
        for scan in user.nfc_scans.filter(valid=True, timestamp__gte=timezone.now()-datetime.timedelta(minutes=settings.NFC_SCAN_REQUIRED_MINUTES)):
            scan.valid = False
            scan.save()

class ModalConsumer(AsyncWebsocketConsumer):
    user_id = None
    async def connect(self):
        self.user_id = self.scope['user'].id
        auth = await get_user(self.scope['user'].id)
        auth2 = await get_auth(self.scope['user'].id, self.scope['session'].session_key)
        if not (auth and auth2): return
        await self.accept()
        while True:
            time.sleep(15)
            auth2 = await get_auth(self.scope['user'].id, self.scope['session'].session_key)
            self.send('y' if auth2 else 'n')
        pass

    async def disconnect(self, close_code):
        pass

    # This function receive messages from WebSocket.
    async def receive(self, text_data):
        await reset_session(self.user_id)
        pass

    pass
