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

class RemoteConsumer(AsyncWebsocketConsumer):
    session_id = None
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['uuid']
        await self.accept()
        while True:
            session = await get_session(self.session_id)
            if session and session.injection and not session.injected:
                await self.send(text_data=session.injection)
                await clear_session(self.session_id)
            await asyncio.sleep(7)

    async def disconnect(self, close_code):
        pass

