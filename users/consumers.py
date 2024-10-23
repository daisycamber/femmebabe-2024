from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import time
import asyncio
import threading

@sync_to_async
def get_user(id):
    from django.contrib.auth.models import User
    try:
        user = User.objects.filter(id=int(id)).first()
        if user is None: return False
    except: return False
    return True

async def user_event(self):
    await asyncio.sleep(15)
    auth = await get_user(self.scope['user'].id)
    if auth: await self.send(text_data='y')

async def user_thread(self):
    while self.connected:
        await user_event(self)
        await asyncio.sleep(20)

class AuthConsumer(AsyncWebsocketConsumer):
    connected = False
    async def connect(self):
        await self.accept()
        self.connected = True
        await user_thread(self)
#        t = threading.Thread(target=user_thread, args=(self,))
#        t.start()
        pass

    async def disconnect(self, close_code):
        self.connected = False
        pass

    # This function receive messages from WebSocket.
    async def receive(self, text_data):
        pass

    pass
