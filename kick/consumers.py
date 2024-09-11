import json
from channels.generic.websocket import AsyncWebsocketConsumer
import time
from django.conf import settings
import threading
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
import asyncio

@sync_to_async
def should_kick(user_id, session_key):
    user = None
    try:
        user = User.objects.get(id=int(user_id))
    except: pass
    from django.contrib.sessions.models import Session
    from django.shortcuts import render, redirect
    from django.http import HttpResponse
    from security.models import Session, UserIpAddress
    from django.contrib.auth import logout
    from security.apis import check_ip_risk, get_client_ip
    from django.urls import reverse
    from django.contrib import messages
    from .forms import AppealForm
    from feed.templatetags.nts import number_to_string
    if user and not user.profile.kick:
        return 'n'
    ip = get_client_ip(request)
    from security.security import fraud_detect
    from kick.views import is_kick
    if user and is_kick(ip, user) or fraud_detect(list([ip, user])):
        try:
            [s.delete() for s in Session.objects.all() if s.get_decoded().get('_auth_user_id') == user.id and s.session_key == session_key]
        except: pass
        logout(request)
        return 'y'
    return 'n'

async def run_kick(self):
    auth2 = await should_kick(self.scope['user'].id, self.scope['session'].session_key)
    self.send(text_data='y' if auth2 else 'n')

async def kick_thread(self):
    while self.connected:
        await run_kick(self)
        await asyncio.sleep(settings.ASSESS_KICK_INTERVAL)

class KickConsumer(AsyncWebsocketConsumer):
    user_id = None
    session_key = None
    ip = None
    connected = False
    async def connect(self):
        self.user_id = self.scope['user'].id
        self.session_key = self.scope['session'].session_key
        self.ip = self.scope["client"][0]
        await self.accept()
        self.connected = True
        await kick_thread(self)

    async def disconnect(self, close_code):
        self.connected = False
        pass

    # This function receive messages from WebSocket.
    async def receive(self, text_data):
        pass

    pass
