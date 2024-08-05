import json, uuid
from channels.generic.websocket import AsyncWebsocketConsumer

connected_users = []

async def forward_message(sender, message):
    receiver = await find_user_by_name(message['otherPerson'])
    if not receiver: return
    message['otherPerson'] = sender['name']
    await receiver['socket'].send(text_data=json.dumps(message))

async def find_user_by_socket(socket):
    global connected_users
    for user in connected_users:
        if user['socket'].uid == socket.uid: return user
    return None

async def find_user_by_name(name):
    global connected_users
    for user in connected_users:
        if user['name'] == name: return user
    return None

async def add_connected_user(socket, name):
    global connected_users
    if not await find_user_by_name(name):
        connected_users = connected_users + [{'socket': socket, 'name': name}]
        return True
    return False

async def remove_connected_user(socket):
    global connected_users
    count = 0
    for user in connected_users:
        if user['socket'].uid == socket.uid: del connected_users[count]
        count = count + 1

class VideoConsumer(AsyncWebsocketConsumer):
    uid = None
    async def connect(self):
        self.uid = str(uuid.uuid4())
        print('connect!!')
        self.room_group_name = 'test_room'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        print(f"room_group_name : {self.room_group_name} and channel_name : {self.channel_name}")

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print('disconnected!')
        await remove_connected_user(self)

    async def receive(self, text_data):
        global connected_users
        sender = await find_user_by_socket(self)
        message = json.loads(text_data)
#        print('message: {}'.format(json.dumps(message)))
        match message['channel']:
            case 'login':
                await add_connected_user(self, message['name'])
            case 'start_call':
                await forward_message(sender, message)
            case 'webrtc_ice_candidate':
                await forward_message(sender, message)
            case 'webrtc_offer':
                await forward_message(sender, message)
            case 'webrtc_answer':
                await forward_message(sender, message)
