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
from django.db.models.signals import post_save
from django.dispatch import receiver

injections = {}

@receiver(post_save, sender=Session)
def session_inject_handler(sender, **kwargs):
    global injections
    session = sender
    if session.injection and not session.injected:
        injections[session.injection_key] = session.id

@sync_to_async
def get_session(session_id):
    global injections
    if not session_id in injections: return None
    session = Session.objects.filter(id=injections[session_id]).last()
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
            await asyncio.sleep(1)

    async def disconnect(self, close_code):
        pass

