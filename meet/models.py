from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.utils import timezone

def get_code():
    return get_random_string(length=12)

class Meeting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meetings')
    code = models.CharField(max_length=16, default=get_code)
    start_time = models.DateTimeField(default=timezone.now)

class Attendee(models.Model):
    upload_url = models.CharField(max_length=1000, default='')
    video_url = models.CharField(max_length=1000, default='')
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='attendees')

