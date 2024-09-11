from datetime import datetime, time
from django.conf import settings

def audio_context(request):
    context_data = dict()
    context_data['audio_interval'] = settings.AUDIO_LIVE_INTERVAL
    return context_data
