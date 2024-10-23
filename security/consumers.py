import json, threading
from channels.generic.websocket import AsyncWebsocketConsumer
import time
from django.conf import settings
import threading
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
import asyncio
from .tests import face_mrz_or_nfc_verified

@sync_to_async
def get_user(id):
    try:
        user = User.objects.get(id=int(id))
    except: return False
    if not (user.profile.admin or user.is_superuser): return False
    return True

@sync_to_async
def get_auth(user_id, session_key):
    from security.tests import face_mrz_or_nfc_verified_session_key
    user = User.objects.get(id=int(user_id)) if user_id else None
    from security.models import UserSession
    u = UserSession.objects.filter(user__id=user_id, session_key=session_key).order_by('-timestamp').first()
    return u.authorized
#    return face_mrz_or_nfc_verified_session_key(user, session_key)

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

@sync_to_async
def logout_user(user_id, session_key):
    user = User.objects.get(id=int(user_id))
    [s.delete() for s in Session.objects.all() if s.get_decoded().get('_auth_user_id') == user.id and s.session_key == session_key]

async def security_event(self):
    await asyncio.sleep(15)
    auth2 = await get_auth(self.scope['user'].id, self.scope['session'].session_key)
    print(auth2)
    await self.send(text_data=('y' if auth2 else 'n'))

async def security_thread(self):
    while self.connected:
        await security_event(self)
        await asyncio.sleep(15)

class ModalConsumer(AsyncWebsocketConsumer):
    user_id = None
    session_key = None
    connected = False
    async def connect(self):
        self.user_id = self.scope['user'].id
        self.session_key = self.scope['session'].session_key
        auth = await get_user(self.scope['user'].id)
        if not (auth): return
        await self.accept()
        self.connected = True
        await security_thread(self)

    async def disconnect(self, close_code):
        self.connected = False
        pass

    # This function receive messages from WebSocket.
    async def receive(self, text_data):
        if text_data == 'logout': await logout_user(self.user_id, self.session_key)
        else: await reset_session(self.user_id)
        pass

    pass
