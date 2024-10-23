import json
from channels.generic.websocket import AsyncWebsocketConsumer
import re
import os
import sys
import select
import paramiko
import time
from django.conf import settings
import threading, multiprocessing
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
import asyncio
from security.models import Session
from errors.highlight import highlight_code, highlight_shell
from shell.run import shell_fix
from urllib.parse import parse_qs

retry_time = 60 * 2

host_ip = '127.0.0.1'
host_port = 21879

@sync_to_async
def get_user(id):
    user = User.objects.get(id=int(id))
    if not (user.profile.admin or user.is_superuser): return False
    return True

@sync_to_async
def check_token(user_id, token):
    user = User.objects.get(id=int(user_id))
    import urllib.parse
    from security.crypto import decrypt
    return user.profile.check_shell_token(decrypt(urllib.parse.unquote(token)))

@sync_to_async
def get_auth(user_id, session_key):
#    from security.tests import face_mrz_or_nfc_verified_session_key
#    user = User.objects.get(id=int(user_id)) if user_id else None
#    print('Verified? ' + str(face_mrz_or_nfc_verified_session_key(user, session_key)))
#    return face_mrz_or_nfc_verified_session_key(user, session_key) != False
    from security.models import UserSession
    sess = UserSession.objects.filter(user__id=user_id, session_key=session_key).order_by('-timestamp')
    for s in sess:
        if s.authorized: return True
    return False

@sync_to_async
def get_req(scope):
    user = User.objects.get(id=scope['user'].id)
    ip = scope['client'][0]
    path = scope['path']
    print(ip)
    s = Session.objects.create(user=user, ip_address=ip, path=path)
    from django.utils import timezone
    import datetime
    sessions = Session.objects.filter(user=user, ip_address=ip, path=path, time__gte=timezone.now() - datetime.timedelta(seconds=4))
    if sessions.count() > 1: return False
    if sessions.count() < 1: return False
    return True

async def send(channel, output):
    await channel.send(text_data=output)

def terminal_thread(self, channel):
    while self.connected:
        while not channel.recv_ready():
            asyncio.sleep(0.05)
        read = True
        output = ""
        while read:
            read = False
            if channel.recv_ready():
                rl, wl, xl = select.select([ channel ], [ ], [ ], 0.0)
                if len(rl) > 0:
                    tmp = channel.recv(99999)
                    output = output + tmp.decode()
                    read = True
                    asyncio.sleep(0.05)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        from security.crypto import encrypt
        import urllib.parse
        loop.run_until_complete(send(self, urllib.parse.quote(encrypt(output, secret=self.token))))
        loop.close()

@sync_to_async
def receive_data(self, text_data):
    from security.crypto import decrypt
    import urllib.parse
    self.channel.send(decrypt(urllib.parse.unquote(text_data), secret=self.token))


class TerminalConsumer(AsyncWebsocketConsumer):
    channel = None
    rows = None
    cols = None
    connected = False
    token = None
    x = None
    async def connect(self):
        query_params = parse_qs(self.scope["query_string"].decode())
        auth = await get_user(self.scope['user'].id)
        import urllib.parse
        token = await check_token(self.scope['user'].id, query_params['token'][0])
        auth2 = await get_auth(self.scope['user'].id, self.scope['session'].session_key)
        print('Auth 1? {}'.format(str(auth)))
        print('Auth 2? {}'.format(str(auth2)))
        if not token:
            print('Token invalid for shell')
            return
#        auth3 = await get_req(self.scope)
        if not (auth and auth2): return
        if 'rows' in query_params and query_params['rows']: self.rows = int(query_params.get('rows', '28')[0])
        if 'cols' in query_params and query_params['cols']: self.cols = int(query_params.get('cols', '32')[0])
        await self.accept()
#        self.send(query_params['token'])
        self.connected = True
        i = 0
        ssh = None
        while self.connected:
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client = paramiko.SSHClient()
                pkey = paramiko.RSAKey.from_private_key_file("/home/{}/.ssh/id_rsa".format(settings.BASH_USER))
                ssh.connect(host_ip, port=host_port, username=settings.BASH_USER, password=settings.BASH_PASS, pkey=pkey)
                break
            except paramiko.AuthenticationException:
                print("Authentication failed when connecting to %s" % host_ip)
                pass
            except:
                print("Could not SSH to %s, waiting for it to start" % host_ip)
                i += 1
                asyncio.sleep(2)
                # If we could not connect within time limit
                if i >= retry_time:
                    print("Could not connect to %s. Giving up" % host_ip)
                    return None
        self.ssh = ssh
        self.channel = ssh.invoke_shell(width=self.cols, height=self.rows)
#        await terminal_thread(self, self.channel)
#        multiprocessing.Process(target=terminal_thread, args=(self, self.channel)).start()
        pass

    async def disconnect(self, close_code):
        if hasattr(self, 'ssh') and self.ssh: self.ssh.close()
        self.connected = False
        pass

    # This function receive messages from WebSocket.
    async def receive(self, text_data):
        if not self.token:
            self.token = text_data
            self.x = threading.Thread(target=terminal_thread, args=(self,self.channel,))
            self.x.start()
            return
        await receive_data(self, text_data)
        pass

    pass

def shell_thread(self, channel):
    while self.connected:
        while not channel.recv_ready():
            asyncio.sleep(0.1)
        read = True
        output = ""
        while read:
            read = False
            if channel.recv_ready():
                rl, wl, xl = select.select([ channel ], [ ], [ ], 0.0)
                if len(rl) > 0:
                    tmp = channel.recv(999999999)
                    output = output + tmp.decode()
                    read = True
                    asyncio.sleep(0.1)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        from security.crypto import encrypt
        import urllib.parse
        loop.run_until_complete(send(self, urllib.parse.quote(encrypt(highlight_shell(shell_fix(output)), secret=self.key))))
        loop.close()

@sync_to_async
def receive_data_shell(self, text_data):
    from security.crypto import encrypt, decrypt
    import urllib.parse
    print('Key: {}'.format(self.key))
    command = decrypt(urllib.parse.unquote(text_data), secret=self.key)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    if command == 'reload':
        output = highlight_code(safe_reload())
        loop.run_until_complete(send(self, urllib.parse.quote(encrypt(output, secret=self.key))))
    elif command.split(' ')[0] == 'clear':
        output = '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n'
        loop.run_until_complete(send(self, urllib.parse.quote(encrypt(output, secret=self.key))))
    elif command.split(' ')[0] == 'nano':
        file = command.split(' ')[1]
        output = '$ ' + command + '\n<iframe src="/shell/edit/?hidenavbar=t&path=' + file + '" width="100%;" height="690px;"></iframe>'
        loop.run_until_complete(send(self, urllib.parse.quote(encrypt(output, secret=self.key))))
    elif command.split(' ')[0] == 'cancel':
        self.channel.send("\x03")
    else:
        self.channel.send(command + '\n')

class ShellConsumer(AsyncWebsocketConsumer):
    channel = None
    connected = False
    key = None
    x = None
    async def connect(self):
        query_params = parse_qs(self.scope["query_string"].decode())
        auth = await get_user(self.scope['user'].id)
        token = await check_token(self.scope['user'].id, query_params['token'][0])
        if not token: return
        auth2 = await get_auth(self.scope['user'].id, self.scope['session'].session_key)
#        auth3 = await get_req(self.scope)
        if not (auth and auth2): return
        await self.accept()
        self.connected = True
        i = 0
        ssh = None
        while self.connected:
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client = paramiko.SSHClient()
                pkey = paramiko.RSAKey.from_private_key_file("/home/{}/.ssh/id_rsa".format(settings.BASH_USER))
                ssh.connect(host_ip, port=host_port, username=settings.BASH_USER, password=settings.BASH_PASS, pkey=pkey)
                break
            except paramiko.AuthenticationException:
                print("Authentication failed when connecting to %s" % host_ip)
                pass
            except:
                print("Could not SSH to %s, waiting for it to start" % host_ip)
                i += 1
                asyncio.sleep(2)
                # If we could not connect within time limit
                if i >= retry_time:
                    print("Could not connect to %s. Giving up" % host_ip)
                    return None
        self.ssh = ssh
        self.channel = ssh.invoke_shell(width=120, height=50)
        pass

    async def disconnect(self, close_code):
        if hasattr(self, 'ssh') and self.ssh: self.ssh.close()
        self.connected = False
        pass

    # This function receive messages from WebSocket.
    async def receive(self, text_data):
        command = text_data
        if not self.key:
            self.key = text_data
            self.x = threading.Thread(target=shell_thread, args=(self,self.channel,))
            self.x.start()
            return
        await receive_data_shell(self, text_data)
        pass

    pass
