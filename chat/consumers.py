import json
from channels.generic.websocket import AsyncWebsocketConsumer
import re
import os
import sys
import select
from django.conf import settings
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from django.template.loader import render_to_string
from .models import Message
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from users.models import Profile
import datetime
from django.core.paginator import Paginator

@sync_to_async
def get_chat(user_id, recipient_id, lang='en'):
    user = User.objects.get(id=int(user_id))
    recipient = User.objects.get(id=int(recipient_id))
    page = 1
    msgs = None
    new = False
    if recipient == user:
        msgs = Message.objects.filter(recipient=recipient).order_by('-sent_at')
    else:
        msgs = Message.objects.filter(sender=recipient).union(Message.objects.filter(sender=user)).order_by('-sent_at')
    p = Paginator(msgs, 10)
    for m in p.get_page(page):
        if (m.sender == user and m.senderseen == False) or m.seen == False:
            new = True
    if new:
        page = 1
        p = Paginator(msgs, 10)
        for message in p.page(page):
            message.lang = lang
            if message.recipient == user:
                message.seen = True
                message.save()
            if message.sender == user:
                message.senderseen = True
                message.save()
        context = {
            'messages': p.page(page),
            'count': p.count,
            'page_obj': p.get_page(page),
        }
        text = render_to_string('chat/messages_raw.html', context)
        return text
    return False

@sync_to_async
def get_chat_user(name):
    return User.objects.get(profile__name=name)

@sync_to_async
def get_user(user_id):
    return User.objects.get(id=user_id)

async def chat_event(self):
    chat = await get_chat(self.scope['user'].id, self.chat_user.id)
    if chat:
        await self.send(text_data=chat)

async def chat_thread(self):
    while self.connected:
        await chat_event(self)
        await asyncio.sleep(15)

# Send the setting to the server from foreign user
class ChatConsumer(AsyncWebsocketConsumer):
    chat_user = None
    connected = False
    async def connect(self):
        self.chat_user = await get_chat_user(self.scope['url_route']['kwargs']['username'])
        await self.accept()
        self.connected = True
        user = await get_user(self.scope['user'].id)
        await chat_thread(self)

    async def disconnect(self, close_code):
        self.connected = False
        pass

    # This function receive messages from WebSocket.
    async def receive(self, text_data):
        pass
    pass
