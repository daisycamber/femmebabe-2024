from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid, random
import datetime
import pytz
from django.conf import settings
import os, shutil
from .apis import is_safe
from security.secure import get_secure_video_path, get_secure_still_path, get_secure_live_path
from django.urls import reverse
from .still import get_still
from feed.middleware import get_current_user
from feed.crop import crop_center
from feed.storage import MediaStorage
from feed.nude import is_nude

DEFAULT_CAMERA_NAME = 'private'

def idle_recording(username):
    recordings = VideoRecording.objects.filter(user__username=username, interactive='idle')
    if recordings.count() == 0: return None
    recording = recordings[random.randint(0, recordings.count()-1)]
    return recording

def idle_frame(username):
    recording = idle_recording(username)
    if not recording: return None
    frame = recording.frames.all()[math.random(0, recording.frames.count()-1)]
    return frame

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % ('{}-{}-{}'.format(uuid.uuid4(), instance.last_frame.strftime("%Y%m%d-%H%M%S") if hasattr(instance, 'last_frame') else instance.time_captured.strftime("%Y%m%d-%H%M%S") if hasattr(instance, 'time_captured') else 'n-n', get_current_user().id if get_current_user() else '0'), ext)
    return os.path.join('live/files/', filename)

def get_stream_path():
    ext = 'm3u8'
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('live/stream/', filename)

def get_still_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % ('{}-{}-{}'.format(uuid.uuid4(), instance.last_frame.strftime("%Y%m%d-%H%M%S") if hasattr(instance, 'last_frame') else instance.time_captured.strftime("%Y%m%d-%H%M%S") if hasattr(instance, 'time_captured') else '0', get_current_user().id if get_current_user() else '0'), ext)
    return os.path.join('live/stills/', filename)

class UploadProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='live_profiles')
    tiktok_code = models.CharField(default='', null=True, blank=True, max_length=100)

class Show(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='user_shows')
    model = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='model_shows')
    start = models.DateTimeField(default=timezone.now)
    end = models.DateTimeField(default=timezone.now)

class Camera(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='camera')
    src = models.TextField(default="", null=True, blank=True)
    thumbnail = models.TextField(default="", null=True, blank=True)
    last_frame = models.DateTimeField(default=timezone.now)

class VideoFrame(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='video_frames')
    confirmation_id = models.TextField(default="", null=True, blank=True)
    frame = models.FileField(upload_to=get_file_path, null=True, blank=True)
    still = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    still_bucket = models.FileField(upload_to=get_file_path, storage=MediaStorage(), null=True, blank=True)
    still_thumbnail = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    still_thumbnail_bucket = models.FileField(upload_to=get_file_path, storage=MediaStorage(), null=True, blank=True)
    time_captured = models.DateTimeField(default=timezone.now)
    time_uploaded = models.DateTimeField(default=timezone.now)
    compressed = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    pitch_adjust = models.IntegerField(default=0)
    safe = models.BooleanField(default=True)
    public = models.BooleanField(default=False)
    difference = models.FloatField(default=0)

    def get_still_thumb_url(self, url=True):
        from PIL import Image
        if self.still_thumbnail_bucket: return self.still_thumbnail_bucket.url
        if not self.still or not os.path.exists(self.still.path):
            path = os.path.join(settings.BASE_DIR, 'media', get_still_path(self, self.frame.name + '.jpg'))
            get_still(self.frame.path, path)
            self.still = path
            self.save()
        if self.still and not self.still_thumbnail or not os.path.exists(self.still_thumbnail.path):
            path = os.path.join('media', get_still_path(self, self.frame.name + '.jpg'))
            full_path = os.path.join(settings.BASE_DIR, path)
            try:
                shutil.copy(self.still.path, full_path)
            except: return ''
            self.still_thumbnail = full_path
            img = Image.open(self.still_thumbnail.path)
            if img:
                if img.height > settings.THUMB_IMAGE_DIMENSION or img.width > settings.THUMB_IMAGE_DIMENSION:
                    output_size = (settings.THUMB_IMAGE_DIMENSION, settings.THUMB_IMAGE_DIMENSION)
                    max = img.width
                    if img.height < img.width:
                        max = img.height
                    img = crop_center(img,max,max)
                    img.save(self.still_thumbnail.path, 'png')
                    img = Image.open(self.still_thumbnail.path)
                    img.thumbnail(output_size)
                    img.save(self.still_thumbnail.path)
        if not url: return

        path, url = get_secure_still_path(self.still_thumbnail.name)
        full_path = os.path.join(settings.BASE_DIR, path)
        shutil.copy(self.still_thumbnail.path, full_path)
        from lotteh.celery import remove_secure
        remove_secure.apply_async([full_path], countdown=settings.REMOVE_SECURE_STILL_TIMEOUT_SECONDS)
        return reverse('live:still', kwargs={'filename': url})

    def delete_video(self):
        try:
            os.remove(self.frame.path)
            self.frame = None
        except: pass
        try:
            os.remove(self.still.path)
            self.still = None
        except: pass
        try:
            os.remove(self.still_thumbnail.path)
            self.still_thumbnail = None
        except: pass
        self.save()

    def get_still_url(self, url=True):
        if self.still_bucket: return self.still_bucket.url
        if not self.still or not os.path.exists(self.still.path):
            path = os.path.join(settings.BASE_DIR, 'media', get_still_path(self, self.frame.name + '.jpg'))
            get_still(self.frame.path, path)
            self.still = path
            try:
                self.safe = not is_nude(path)
            except: self.safe = False
            self.save()
        if not url: return
        path, url = get_secure_still_path(self.still.name)
        full_path = os.path.join(settings.BASE_DIR, path)
        shutil.copy(self.still.path, full_path)
        from lotteh.celery import remove_secure
        remove_secure.apply_async([full_path], countdown=settings.REMOVE_SECURE_STILL_TIMEOUT_SECONDS)
        return reverse('live:still', kwargs={'filename': url})

    def get_frame_url(self):
        path, url = get_secure_live_path(self.frame.name)
        full_path = os.path.join(settings.BASE_DIR, path)
        shutil.copy(self.frame.path, full_path)
        from lotteh.celery import remove_secure
        remove_secure.apply_async([full_path], countdown=settings.REMOVE_SECURE_TIMEOUT_VIDEO_SECONDS)
        return reverse('live:stream-secure-video', kwargs={'filename': url})

    def __str__(self):
        return 'user {}, captured on {}'.format(self.user.profile.name, self.time_captured.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime("%m/%d/%Y at %H:%M:%S"))

    def review(self):
        if self.frame and not is_safe(self.frame.path):
            os.remove(self.frame.path)
            os.remove(self.still.path)
            try:
                os.remove(self.still_thumbnail.path)
            except: pass
            f = idle_frame(self.user.username)
            frame = f.frame if f else None
            self.frame = frame
            self.still = f.still
            self.still_thumbnail = None
            self.save()
            cameras = VideoCamera.objects.filter(user=self.user)
            for camera in cameras:
                os.remove(camera.frame.path)
                os.remove(camera.still.path)
                camera.frame = frame.frame
                camera.still = frame.still
                camera.save()
            print("Deleted unsafe object - " + str(self))

class VideoCamera(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='video_camera')
    name = models.CharField(default=DEFAULT_CAMERA_NAME, null=True, blank=True, max_length=100)
    frame = models.FileField(upload_to=get_file_path, null=True, blank=True)
    frames = models.ManyToManyField(VideoFrame, blank=True, related_name='camera')
    stream = models.FileField(upload_to=get_file_path, default=get_stream_path, null=True, blank=True)
    still = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    width = models.CharField(max_length=10, default="1920")
    last_frame = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(default=timezone.now)
    echo_cancellation = models.BooleanField(default=False)
    compress_video = models.BooleanField(default=False)
    public = models.BooleanField(default=True)
    live = models.BooleanField(default=True)
    recording = models.BooleanField(default=False)
    use_websocket = models.BooleanField(default=False)
    key = models.TextField(default='', blank=True)
    frame_count = models.IntegerField(default=0)
    confirmation_id = models.TextField(default="", null=True, blank=True)
    mime = models.CharField(max_length=10, default="mp4")
    title = models.CharField(max_length=200, default='{}'.format(settings.SITE_NAME))
    description = models.CharField(max_length=1000, default="{} is live at {}".format(settings.SITE_NAME, settings.DOMAIN))
    tags = models.CharField(max_length=500, default="technology,software,web development,machine learning,artificial intelligence,beauty,fashion,makeup,model,celebrity")
    default = models.BooleanField(default=False)
    upload = models.BooleanField(default=False)
    muted = models.BooleanField(default=False)

    def __str__(self):
        return '@{} - "{}", last recorded {}'.format(self.user.profile.name, self.name, self.last_frame.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%B %d, %Y %H:%M:%S'))

    def get_file_url(self):
        return reverse('live:stream-video', kwargs={'filename': self.frame.name.split('/')[-1]})

    def get_frame_url(self):
        path, url = get_secure_live_path(self.frame.name)
        full_path = os.path.join(settings.BASE_DIR, path)
        shutil.copy(self.frame.path, full_path)
        from lotteh.celery import remove_secure
        remove_secure.apply_async([full_path], countdown=settings.REMOVE_SECURE_TIMEOUT_VIDEO_SECONDS)
        return reverse('live:stream-secure-video', kwargs={'filename': url})

    def get_still_url(self):
        if not self.still:
            path = os.path.join(settings.BASE_DIR, 'media', get_still_path(self, self.frame.name))
            self.still = get_still(self.frame.path + '.jpg', path)
            self.save()
        path, url = get_secure_still_path(self.frame.path + '.jpg')
        full_path = os.path.join(settings.BASE_DIR, path)
        try:
            shutil.copy(self.still.path, full_path)
        except:
            self.still = get_still(self.frame.path + '.jpg', path)
            self.save()
        from lotteh.celery import remove_secure
        remove_secure.apply_async([full_path], countdown=settings.REMOVE_SECURE_TIMEOUT_SECONDS)
        return reverse('live:still', kwargs={'filename': url})

    def short_time(self):
        return self.last_frame.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%H:%M:%S')

    def review(self):
        if self.frame and not is_safe(os.path.join(settings.BASE_DIR, 'media', self.frame.path)):
            self.public = False
            self.save()
            f = idle_frame(self.user.username)
            frame = f.frame if hasattr(f, 'frame') else None
            still = f.still if hasattr(f, 'still') else None
            self.frame = frame
            self.still = still
            self.save()
            print("Deleted unsafe object - " + str(self))

    def save(self, *args, **kwargs):
        try:
            camera = VideoCamera.objects.get(user=self.user)
            if camera.frame != self.frame and self.frame and self.frame.path != str(os.path.join(settings.BASE_DIR,'/media/frame.webm')):
                from lotteh.celery import delay_remove
                delay_remove.apply_async([camera.frame.path], countdown=30)
                delay_remove.apply_async([camera.frame.still], countdown=30)
        except: pass
        super(VideoCamera, self).save(*args, **kwargs)


class VideoRecording(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='video_recordings')
    frames = models.ManyToManyField(VideoFrame, blank=True)
    file = models.FileField(upload_to=get_file_path, null=True, blank=True)
    file_processed = models.FileField(upload_to=get_file_path, storage=MediaStorage(), null=True, blank=True)
    uuid = models.CharField(max_length=100, default=uuid.uuid4)
    camera = models.CharField(max_length=100, default=DEFAULT_CAMERA_NAME)
    last_frame = models.DateTimeField(default=timezone.now)
    compressed = models.BooleanField(default=False)
    public = models.BooleanField(default=True)
    processing = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    interactive = models.CharField(max_length=100, default='', blank=True)
    transcript = models.TextField(default='', blank=True)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='received_recordings')
    uploaded = models.BooleanField(default=False)
    safe = models.BooleanField(default=False)


    def get_file_url(self):
        if self.file_processed: return self.file_processed.url
        path, url = get_secure_live_path(self.file.name)
        full_path = os.path.join(settings.BASE_DIR, path)
        shutil.copy(self.file.path, full_path)
        from lotteh.celery import remove_secure
        remove_secure.apply_async([full_path], countdown=settings.REMOVE_SECURE_TIMEOUT_FILE_SECONDS)
        return reverse('live:stream-secure-video', kwargs={'filename': url})

    def __str__(self):
        return 'Last frame at {}, Interactive "{}", public = {}'.format(self.last_frame.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime("%m/%d/%Y, %H:%M:%S"), self.interactive, self.public)

    def save(self, *args, **kwargs):
        from .concat import concat
#        old = VideoRecording.objects.filter(id=self.id).first()
#        if old and old.frames != self.frames and old.processed and self.file == old.file:
#            path = os.path.join(settings.BASE_DIR, 'media', get_file_path(recording, 'file.webm'))
#            os.remove(self.file.path)
#            self.file = concat(self, path)
        super(VideoRecording, self).save(*args, **kwargs)

    def delete(self):
        for frame in self.frames.all():
            if frame.frame:
                try:
                    os.remove(frame.frame.path)
                except: pass
        if self.file:
            try:
                os.remove(self.file.path)
            except: pass
        super(VideoRecording, self).delete()

    def short_time(self):
        return self.last_frame.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%H:%M:%S')
