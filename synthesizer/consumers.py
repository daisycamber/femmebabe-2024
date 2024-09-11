
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import re
import os
import sys
import select
from django.conf import settings
from django.contrib.auth.models import User
from live.models import VideoCamera
from asgiref.sync import sync_to_async
import pytz, datetime
from django.utils import timezone
from django.conf import settings
import base64
import urllib.parse
from .models import Project, Midi, Note

@sync_to_async
def update_note(project_id, midi_id, note_data):
    project = Project.objects.filter(identifier=project_id)
    midi = Midi.objects.get_or_create(id=midi_id)
    split = note_data.split(',')
    pitch = split[0]
    length = split[1]
    lndex = split[2]
    note = midi.notes.filter(pitch=pitch, length=int(length), index=index)
    if note:
        note.delete()
    else:
        note = midi.notes.create(pitch=note, length=int(length), index=index)
    return midi.id

@sync_to_async
def update_position(project_id, midi_id, pos_data):
    project = Project.objects.filter(identifier=project_id)
    midi = Midi.objects.get_or_create(id=midi_id)
    split = pos_data.split(',')
    track = split[0]
    length = split[1]
    lndex = split[2]
    pos = midi.position.filter(track=track, length=int(length), index=index)
    if pos:
        pos.delete()
    else:
        pos = midi.position.create(track=track, length=int(length), index=index)
    return pos.id

@sync_to_async
def update_instrument(project_id, synth_index, data):
    project = Project.objects.filter(identifier=project_id)
    synth = project.synths.all()[synth_index]
    split = data.split(',')
    synth.volume = split[0]
    synth.gain = split[1]
    synth.length = split[2]
    synth.distortion = split[3]
    synth.highpass_filter = split[4]
    synth.lowpass_filter = split[5]
    synth.compressor = split[6]
    synth.delay = split[7]
    synth.reverb = split[8]
    synth.pitch_adjustt = split[9]
    synth.fade = split[10]
    synth.mode = split[11]
    synth.continuous_pitch = split[12]
    synth.enabled = True if split[13] == 'true' else False
    synth.save()

@sync_to_async
def get_user(id, project_id):
    user = User.objects.get(id=int(id))
    if not user.projects.filter(identifier=project_id).first():
        return False
#    if not (user.profile.vendor or user.is_superuser): return False
    return True

@sync_to_async
def get_auth(user_id, session_key):
    from security.tests import face_mrz_or_nfc_verified_session_key
    user = User.objects.get(id=int(user_id)) if user_id else None
    return face_mrz_or_nfc_verified_session_key(user, session_key)

class MidiConsumer(AsyncWebsocketConsumer):
    project_id = None
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project']
        auth = await get_user(self.scope['user'].id, self.project_id)
        auth2 = await get_auth(self.scope['user'].id, self.scope['session'].session_key)
        if not (auth and auth2): return
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        split = text.split(',', 2)
        text = ''
        if text[0] == 'm':
            text = await update_midi(self.project_id, split[1], split[2])
        elif text[0] == 'p':
            text = await update_position(self.project_id, split[1], split[2])
        elif text[0] == 'i':
            text = await update_instrument(self.project_id, split[1], split[2])
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
#        text = await get_camera_status(self.camera_user, self.camera_name)
#        await self.send(text_data=text)

    pass
