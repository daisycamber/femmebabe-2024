from django import forms
import datetime, pytz
from django.utils import timezone
from live.models import VideoCamera, Show
from users.models import Profile
from django.conf import settings
from feed.middleware import get_current_user, get_current_request
from translate.translate import translate

class CameraForm(forms.ModelForm):
    timestamp = forms.CharField(required=True, min_length=1)
    confirmation_id = forms.CharField(widget=forms.HiddenInput())
    def __init__(self, *args, **kwargs):
        super(CameraForm, self).__init__(*args, **kwargs)
    class Meta:
        model = VideoCamera
        fields = ('frame',)

CHOICES = [['320','320x240'],['640','640x480'],['720', '720x640'],['1280','1280x720'],['1920', '1920x1080'],['2560','2560x2048'],['4096','4096x2160']]

class NameCameraForm(forms.ModelForm):
    name = forms.CharField(required=True, min_length=1)
    width = forms.CharField(widget=forms.Select(choices=CHOICES))
    def __init__(self, *args, **kwargs):
        super(NameCameraForm, self).__init__(*args, **kwargs)
        self.fields['width'].label = 'Resolution'
        self.fields['echo_cancellation'].initial = self.instance.echo_cancellation
        self.fields['use_websocket'].initial = self.instance.use_websocket
        self.fields['compress_video'].initial = self.instance.use_websocket
    class Meta:
        model = VideoCamera
        fields = ('name', 'width', 'use_websocket', 'echo_cancellation', 'compress_video', 'default', 'live', 'recording', 'upload', 'title', 'description', 'tags')

class LiveShowForm(forms.ModelForm):
    choice = forms.CharField()
    def __init__(self, *args, **kwargs):
        super(LiveShowForm, self).__init__(*args, **kwargs)
        self.fields['choice'].label = translate(get_current_request(), 'Choose a time for the private show')
        user = self.instance.user
        CHOICES = list()
        for x in range(7):
            date = timezone.now() + datetime.timedelta(hours=24*x)
            for y in range(settings.LIVE_SCHEDULE_HOURS):
                time = datetime.time(settings.LIVE_SCHEDULE_BEGINS + y, 0)
                dt = datetime.datetime.combine(date, time).astimezone(pytz.timezone(settings.TIME_ZONE))
                if dt > timezone.now() + datetime.timedelta(minutes=60) and not Show.objects.filter(start__gte=dt, end__lte=dt + datetime.timedelta(settings.LIVE_SHOW_LENGTH_MINUTES)).first():
                    CHOICES.append((dt.strftime('%m/%d/%Y %H:%M:%S'), translate(get_current_request(), 'On {}'.format(dt.strftime('%B %d, %Y at %-I:%M %p')))))
        self.fields['choice'].widget = forms.Select(choices=CHOICES)
    class Meta:
        model = Profile
        fields = ['choice']

class ChooseCameraForm(forms.Form):
    choice = forms.CharField()
    def __init__(self, *args, **kwargs):
        super(ChooseCameraForm, self).__init__(*args, **kwargs)
        self.fields['choice'].label = 'Choose a camera to begin'
        user = get_current_user()
        cams = VideoCamera.objects.filter(user=user).order_by('-last_frame')
        cameras = []
        for camera in cams:
            if len(camera.name) < 32:
                cameras = cameras + [camera]
        CHOICES = list()
        for camera in cameras:
            CHOICES.append((camera.name,camera.name))
        self.fields['choice'].widget = forms.Select(choices=CHOICES)
        self.fields['choice'].initial = [cameras.first().name]
