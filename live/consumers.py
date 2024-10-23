import json, threading
from channels.generic.websocket import AsyncWebsocketConsumer
import re
import os
import sys
import select
import asyncio
from django.conf import settings
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async

@sync_to_async
def get_camera_data(camera_user, camera_name, index, request_user):
    from live.models import VideoCamera
    from live.models import get_file_path, VideoFrame, VideoRecording, Show
    import pytz, datetime
    from django.utils import timezone
    from django.conf import settings
    import base64, asyncio
    import urllib.parse
    from urllib.parse import parse_qs
    from feed.tests import identity_really_verified
    profile = get_object_or_404(Profile, name=camera_user, identity_verified=True, vendor=True)
    cameras = VideoCamera.objects.filter(user=profile.user, name=camera_name)
    model = User.objects.get(profile__name=username)
    frame = c.frames.filter(processed=True, public=True if profile.user != request_user else None).order_by('time_captured')[index]
    ext = frame.name.split('.')[-1]
    header = 'data:video/{};base64,'.format(ext)
    with open(frame.frame.path, 'rb') as file:
        return header + base64.b64encode(file.read())

@sync_to_async
def get_camera_status(camera_user, camera_name):
    from live.models import VideoCamera
    return '{},{},{}'.format('y' if VideoCamera.objects.filter(name=camera_name, user__profile__name=camera_user).first().live else 'n', 'y' if VideoCamera.objects.filter(name=camera_name, user__profile__name=camera_user).first().recording else 'n', 'y' if VideoCamera.objects.filter(name=camera_name, user__profile__name=camera_user).first().mute else 'n')

@sync_to_async
def update_camera(camera_user, camera_name, camera_data, key=None):
    from live.models import VideoCamera
    from live.models import get_file_path, VideoFrame, VideoRecording, Show
    import pytz, datetime
    from django.utils import timezone
    from django.conf import settings
    import base64, asyncio
    import urllib.parse
    from urllib.parse import parse_qs
    from feed.tests import identity_really_verified
    from live.still import is_still
    from lotteh.celery import process_live, process_recording
    camera = None
    if key:
        camera = VideoCamera.objects.filter(user__profile__name=camera_user, name=camera_name, key=key).first()
        if (not camera) or (not camera.user.profile.vendor): raise PermissionDenied()
    if not identity_really_verified(camera.user): raise PermissionDenied()
    camera.last_frame = timezone.now()
    camera_data = camera_data.split("&")
    timestamp = datetime.datetime.fromtimestamp(int(camera_data[4].split('=', 1)[1]) / 1000, tz=pytz.UTC)
    frame_data = urllib.parse.unquote(camera_data[5].split('=', 1)[1]).split(',')[1]
    path = os.path.join(settings.MEDIA_ROOT, get_file_path(camera, 'frame.webm'))
    with open(path, "wb") as file:
        file.write(base64.b64decode(frame_data))
    file.close()
    is_frame_still, error = is_still(path)
    frame = VideoFrame.objects.create(user=camera.user, time_captured=timestamp, compressed=camera.user.vendor_profile.compress_video, confirmation_id=camera_data[3].split('=', 1)[1], frame=path, difference=error)
    camera.frame = path
    camera.save()
    if camera.recording and not is_frame_still:
        show = Show.objects.filter(start__lte=timezone.now() + datetime.timedelta(minutes=settings.LIVE_SHOW_LENGTH_MINUTES), start__gte=timezone.now()).first()
        recordings = VideoRecording.objects.filter(user=camera.user, camera=camera.name, public=False if Show.objects.filter(start__lte=timezone.now() + datetime.timedelta(minutes=settings.LIVE_SHOW_LENGTH_MINUTES), start__gte=timezone.now()).count() > 0 else True, recipient=show.user if show else None)
        if recordings.count() == 0:
            recording = VideoRecording.objects.create(user=camera.user, camera=camera.name, last_frame=timestamp, public=False if Show.objects.filter(start__lte=timestamp + datetime.timedelta(minutes=settings.LIVE_SHOW_LENGTH_MINUTES), start__gte=timezone.now()).count() > 0 else True, recipient=show.user if show else None)
            recording.save()
        else:
            recording = recordings.last()
        if recording.last_frame < timezone.now() - datetime.timedelta(seconds=int(settings.LIVE_INTERVAL/1000 * 3)) or (recording.frames.first() and ((recording.last_frame - recording.frames.first().time_captured).total_seconds() > settings.RECORDING_LENGTH_SECONDS)):
            recording = VideoRecording.objects.create(user=camera.user, camera=camera.name, last_frame=timestamp, public=False if Show.objects.filter(start__lte=timezone.now() + datetime.timedelta(minutes=settings.LIVE_SHOW_LENGTH_MINUTES), start__gte=timezone.now()).count() > 0 else True, recipient=show.user if show else None, compressed=camera.user.vendor_profile.compress_video)
            recording.save()
    if not camera.recording or is_frame_still:
        delay_remove_frame.apply_async([frame.id], countdown=int(settings.LIVE_INTERVAL/1000*4))
    camera.mime = frame.frame.name.split('.')[1]
#    camera.save()
    camera.frames.add(frame)
    camera.frame_count = camera.frame_count + 1
    camera.save()
    if recording:
        recording.frames.add(frame)
        recording.last_frame = timestamp
        recording.save()
        process_recording.apply_async([recording.id], countdown=settings.LIVE_INTERVAL/1000 * 3)
    else: print('Not saving frame')
    process_live.apply_async([camera.id, frame.id], countdown=settings.LIVE_INTERVAL/1000 * 3)
    print('5 second video uploaded')
    return frame.confirmation_id


@sync_to_async
def get_user(id):
    user = User.objects.get(id=int(id))
#    if not (user.profile.vendor or user.is_superuser): return False
    return True

@sync_to_async
def get_auth(user_id, session_key):
    from security.tests import face_mrz_or_nfc_verified_session_key
    user = User.objects.get(id=int(user_id)) if user_id else None
    return face_mrz_or_nfc_verified_session_key(user, session_key)

class CameraConsumer(AsyncWebsocketConsumer):
    camera_user = None
    camera_name = None
    key = None
    async def connect(self):
        self.camera_user = self.scope['url_route']['kwargs']['username']
        self.camera_name = self.scope['url_route']['kwargs']['name']
        query_params = parse_qs(self.scope["query_string"].decode())
        if 'key' in query_params and query_params['key']: self.key = query_params['key']
#        auth = await get_user(self.scope['user'].id)
#        auth2 = await get_auth(self.scope['user'].id, self.scope['session'].session_key)
#        if not (auth and auth2): return
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text = await update_camera(self.camera_user, self.camera_name, text_data, self.key)
        await self.send(text_data=text)

    pass

class RemoteConsumer(AsyncWebsocketConsumer):
    camera_user = None
    camera_name = None
    async def connect(self):
        self.camera_user = self.scope['url_route']['kwargs']['username']
        self.camera_name = self.scope['url_route']['kwargs']['name']
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text = await get_camera_status(self.camera_user, self.camera_name)
        await self.send(text_data=text)

async def run_updates(self, camera_user, camera_name, index, user):
    text = await get_camera_data(self, camera_user, camera_name, index, user)
    await self.send(text_data=text)
    asyncio.sleep(settings.LIVE_INTERVAL/1000)

async def send_updates(self, camera_user, camera_name, index, user):
    while self.connected:
        await run_updates(self, camera_user, camera_name, index, user)
        await asyncio.sleep(15)

class VideoConsumer(AsyncWebsocketConsumer):
    user = None
    camera_user = None
    camera_name = None
    key = None
    async def connect(self):
        self.user = await get_user(self.scope['user'].id)
        self.camera_user = self.scope['url_route']['kwargs']['username']
        self.camera_name = self.scope['url_route']['kwargs']['name']
        from urllib.parse import parse_qs
        query_params = parse_qs(self.scope["query_string"].decode())
        if 'key' in query_params and query_params['key']: self.key = query_params['key']
        await self.accept()
        index = int(self.key)
        await send_updates(self, self.camera_user, self.camera_name, index, self.user)

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):

        pass
