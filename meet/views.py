from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from users.models import Profile
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from feed.tests import identity_verified
from vendors.tests import is_vendor
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
import uuid
from django.conf import settings
from meet.models import Meeting
from live.generate import get_guest_camera
import datetime

def meeting(request):
    meeting = get_object_or_404(Meeting, code=request.GET.get('code', None), start_time__gte=timezone.now() - datetime.timedelta(minutes=60*24*3))
    participant = meeting.attendees.create()
    participant.upload_url, participant.video_url = get_guest_camera(meeting.user)
    participant.save()
    return render(request, 'meet/meeting.html', {'title': 'Meeting', 'meeting': meeting, 'participant': participant})

@login_required
def new_meeting(request):
    meeting = Meeting.objects.create(user=request.user)
    return render(request, 'meet/code.html', {'title': 'Share link to meeting', 'meeting': meeting})
