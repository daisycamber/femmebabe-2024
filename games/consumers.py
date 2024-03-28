import json
from channels.generic.websocket import AsyncWebsocketConsumer
import re
import os
import sys
import select
import time
from django.conf import settings
from django.contrib.auth.models import User
from games.models import Game
from asgiref.sync import sync_to_async
import datetime

@sync_to_async
def get_game(id, code):
    game = Game.objects.filter(post__id=id, code=code).last()
    if not game: game = Game.objects.filter(post__id=id, uid=code, time__gte=timezone.now() - datetime.timedelta(hours=48)).last()
    return game

@sync_to_async
def clear_game(id, code):
    game = Game.objects.filter(post__id=id, code=code).last()
    if not game: game = Game.objects.filter(post__id=id, uid=code, time__gte=timezone.now() - datetime.timedelta(hours=48)).last()
    game.turn = ''
    game.save()

@sync_to_async
def set_game(uid, code, turn):
    game = Game.objects.filter(post__id=id, code=code).last()
    if not game: game = Game.objects.filter(post__id=id, uid=code, time__gte=timezone.now() - datetime.timedelta(hours=48)).last()
    game.turn = turn
    game.turns = game.turns + turn
    game.save()

@sync_to_async
def get_vibe_user(name):
    return User.objects.get(profile__name=name)

@sync_to_async
def get_user(user_id):
    print(user_id)
    return User.objects.get(id=user_id)

# Send the setting to the server from foreign user
class GameConsumer(AsyncWebsocketConsumer):
    vibe_user = None
    id = None
    code = None
    async def connect(self):
        self.id = self.scope['url_route']['kwargs']['id']
        self.code = self.scope['url_route']['kwargs']['code']
#        self.player = self.scope['url_route']['kwargs']['player']
        await self.accept()
        game = await get_game(self.id, self.code)
        if game.started: await self.send(text_data=game.turns)
        while not game.started:
            await self.send(text_data='x')
            time.sleep(1)
            game = await get_game(self.id, self.code)

    async def disconnect(self, close_code):
        pass

    # This function receive messages from WebSocket.
    async def receive(self, text_data):
        if text_data == 'x':
            game = await get_game(self.id, self.code)
            if game.turn:
                await self.send(text_data=game.turns)
                await clear_game(self.id, self.code)
            pass
        await set_game(self.id, self.code, text_data)
        pass
    pass
