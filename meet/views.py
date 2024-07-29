from feed.tests import identity_verified
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from vendors.tests import is_vendor

def meeting(request):
    from django.shortcuts import render, redirect, get_object_or_404
    import datetime
    from django.utils import timezone
#    from django.core.exceptions import PermissionDenied
    from live.generate import get_guest_camera
    import datetime
    meeting = get_object_or_404(Meeting, code=request.GET.get('code', None), start_time__gte=timezone.now() - datetime.timedelta(minutes=60*24*3))
    participant = meeting.attendees.create()
    participant.upload_url, participant.video_url = get_guest_camera(meeting.user)
    participant.save()
    return render(request, 'meet/meeting.html', {'title': 'Meeting', 'meeting': meeting, 'participant': participant})

@login_required
def new_meeting(request):
    from django.shortcuts import render
    from meet.models import Meeting
    meeting = Meeting.objects.create(user=request.user)
    return render(request, 'meet/code.html', {'title': 'Share link to meeting', 'meeting': meeting})
