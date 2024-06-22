from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

@sync_to_async
def get_user(id):
    from django.contrib.auth.models import User
    try:
        user = User.objects.filter(id=int(id)).first()
        if user is None: return False
    except: return False
    return True

class AuthConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        while True:
            time.sleep(15)
            auth = await get_user(self.scope['user'].id)
            if auth: self.send('y')
        pass

    async def disconnect(self, close_code):
        pass

    # This function receive messages from WebSocket.
    async def receive(self, text_data):
        pass

    pass
