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
from django.utils import timezone
import datetime

@sync_to_async
def get_game(id, code):
    game = Game.objects.filter(post__id=id, code=code, time__gte=timezone.now() - datetime.timedelta(hours=48)).last()
    if not game: game = Game.objects.filter(post__id=id, uid=code, time__gte=timezone.now() - datetime.timedelta(hours=48)).last()
    return game

@sync_to_async
def set_game(id, code, turn):
    game = Game.objects.filter(post__id=id, code=code, time__gte=timezone.now() - datetime.timedelta(hours=48)).last()
    if not game: game = Game.objects.filter(post__id=id, uid=code, time__gte=timezone.now() - datetime.timedelta(hours=48)).last()
    game.turn = turn
    game.turns = game.turns + turn
    game.save()

@sync_to_async
def update_players(game_id, p):
    game = Game.objects.get(id=int(game_id))
    if game.players is None: game.players = 0
    game.players = game.players + p
    game.save()

@sync_to_async
def get_user(user_id):
    print(user_id)
    return User.objects.get(id=user_id)

class GameConsumer(AsyncWebsocketConsumer):
    id = None
    code = None
    last_turn = 'x'
    async def connect(self):
        self.id = int(self.scope['url_route']['kwargs']['id'])
        self.code = self.scope['url_route']['kwargs']['code']
        game = await get_game(self.id, self.code)
        if game.players is None or game.players < 2:
            await self.accept()
            await update_players(game.id, 1)
        else:
            return
        await self.send(text_data=game.turns)

    async def disconnect(self, close_code):
        game = await get_game(self.id, self.code)
        await update_players(game.id, -1)
        pass

    async def receive(self, text_data):
        game = await get_game(self.id, self.code)
        if text_data == 'x':
            await self.send(text_data=game.turns)
            return
        if text_data == 'y':
            await self.send(text_data=game.turn)
            return
        await set_game(self.id, self.code, text_data)
        pass
    pass
