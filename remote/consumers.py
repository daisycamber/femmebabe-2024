import json
from channels.generic.websocket import AsyncWebsocketConsumer
import re
import os
import sys
import select
from django.conf import settings
from django.contrib.auth.models import User
from live.models import VideoCamera
import asyncio
from security.models import Session
from asgiref.sync import sync_to_async
from django.utils import timezone
import datetime

sessions = {}

@sync_to_async
def update_sessions():
    global sessions
    sess = Session.objects.filter(time__gte=timezone.now() - datetime.timedelta(minutes=60*24*7)).exclude(injection_key__in=sessions, injection='')
    for s in sess:
        if not s.injection_key in sessions.keys():
            sessions[s.injection_key] = s

@sync_to_async
def session_is_injection(session_id):
    global sessions
    if session_id in sessions: return True
    return False

@sync_to_async
def get_session(session_id):
    session = Session.objects.filter(injection_key=session_id, time__gte=timezone.now() - datetime.timedelta(minutes=60*24*7)).last()
    return session

@sync_to_async
def clear_session(session_id):
    session = Session.objects.filter(injection_key=session_id).last()
    session.injected = True
    session.past_injections = session.past_injections + session.injection
    session.injection = ''
    session.save()
    global sessions
    sessions[session_id] = None

class RemoteConsumer(AsyncWebsocketConsumer):
    session_id = None
    connected = False
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['uuid']
        await self.accept()
        self.connected = True
        while self.connected:
            await update_sessions()
            inject = await session_is_injection(self.session_id)
            if not inject: continue
            session = await get_session(self.session_id)
            if session and session.injection and not session.injected:
                await self.send(text_data=session.injection)
                await clear_session(self.session_id)
            await asyncio.sleep(10)

    async def disconnect(self, close_code):
        self.connected = False
        pass

