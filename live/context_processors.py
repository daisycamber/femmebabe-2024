from datetime import datetime, time
from django.contrib.auth.models import User
from django.conf import settings
from live.models import VideoCamera
from users.models import Profile

LIVE_COMPRESSED = False

def live_context(request):
    context_data = dict()
    context_data['record_interval'] = '500'
    context_data['video_interval'] =  str(settings.LIVE_INTERVAL)
    context_data['request_timeout'] =  str(1000 * 30)
    context_data['packet_head'] = 100
    context_data['live_add_security'] = True
    return context_data
