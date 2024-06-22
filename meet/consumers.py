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
from live.models import get_file_path, VideoFrame, VideoRecording, Show
import pytz, datetime
from django.utils import timezone
from django.conf import settings
import base64, asyncio
import urllib.parse
from urllib.parse import parse_qs
from django.core.exceptions import PermissionDenied
from feed.tests import identity_really_verified
from meet.models import Meeting

@sync_to_async
def get_meeting_data(code):
    meeting = Meeting.objects.get(code=code)
    video_urls = ''
    for attendee in meeting.attendees.all():
        video_urls = video_urls + attendee.video_url + ','
    return video_urls[:-1]

class MeetingConsumer(AsyncWebsocketConsumer):
    key = None
    async def connect(self):
        query_params = parse_qs(self.scope["query_string"].decode())
        if 'key' in query_params and query_params['key']: self.key = query_params['key']
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text = await get_meeting_data(self.key)
        await self.send(text_data=text)

    pass
