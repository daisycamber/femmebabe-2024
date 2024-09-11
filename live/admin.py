from django.contrib import admin
from .models import VideoRecording, VideoFrame, VideoCamera
# Register your models here.

admin.site.register(VideoRecording)
admin.site.register(VideoFrame)
admin.site.register(VideoCamera)

