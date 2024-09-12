from simple_history.models import HistoricalRecords
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
import pytz
import datetime
from security.secure import get_secure_face_path
import uuid, os, shutil
from feed.storage import MediaStorage

def get_face_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('face/', filename)

from django.core.files.storage import FileSystemStorage
from django.conf import settings


class FaceStorage(FileSystemStorage):
    def __init__(self, location=None):
        super(FaceStorage, self).__init__(location)

    def url(self, name):
        object = Face.objects.get(image=name)
        url = super(FaceStorage, self).url(name)
        return object.get_secure_url() if not object.image_bucket else object.image_bucket.url

fs = FaceStorage()

# Create your models here.
class Face(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(default=timezone.now)
    image = models.ImageField(default=None, null=True, blank=True, upload_to=get_face_path, storage=fs)
    image_bucket = models.ImageField(default=None, null=True, blank=True, upload_to=get_face_path, storage=MediaStorage())
    hash = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='faces', null=True, blank=True)
    auth_url = models.TextField(blank=True, default='')
    token = models.TextField(blank=True, default='')
    session_key = models.CharField(max_length=100, default='', null=True, blank=True)
    authorized = models.BooleanField(default=False)
    authentic = models.BooleanField(default=False)

    def get_secure_url(self):
        path, url = get_secure_face_path(self.image.name)
        full_path = os.path.join(settings.BASE_DIR, path)
        shutil.copy(self.image.path, full_path)
        from lotteh.celery import remove_secure
        remove_secure.apply_async([full_path], countdown=60*5)
        return url

    def rotate_align(self):
        from feed.align import face_angle_detect
        from PIL import Image
        angle = face_angle_detect(self.image.path)
        img = Image.open(self.image.path)
        img = img.rotate(angle,expand=1)
        img.save(self.image.path)

    def rotate_right(self):
        from PIL import Image
        img = Image.open(self.image.path)
        img = img.rotate(-90,expand=1)
        img.save(self.image.path)
        self.save()

    def rotate_left(self):
        from PIL import Image
        img = Image.open(self.image.path)
        img = img.rotate(90,expand=1)
        img.save(self.image.path)
        self.save()

    def delete(self):
        if self.image:
            os.remove(self.image.path)
        super(Face, self).delete()

    def delete_photo(self):
        if self.image:
            os.remove(self.image.path)
        self.image = None
        self.save()

    def __str__(self):
        return 'user {} face id {} timestamp {}'.format(self.user.username if self.user else 'none', self.id, self.timestamp.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime("%m/%d/%Y at %H:%M:%S"))

    def download_photo(self):
        import os
        from django.conf import settings
        try:
            if self.image and os.path.exists(self.image.path): return
        except: pass
        with self.image_bucket.storage.open(str(self.image_bucket), mode='rb') as bucket_file:
            full_path = os.path.join(settings.BASE_DIR, 'media/', get_face_path(self, 'image.png'))
            with open(full_path, "wb") as image_file:
                image_file.write(bucket_file.read())
            image_file.close()
            self.image = full_path
            self.save()
        bucket_file.close()

    def save(self, *args, **kwargs):
        super(Face, self).save(*args, **kwargs)
        if self.image and not self.image_bucket:
            towrite = self.image_bucket.storage.open(self.image.path, mode='wb')
            with self.image.open('rb') as file:
                towrite.write(file.read())
            self.image_bucket = self.image.path
            from lotteh.celery import delay_remove
            delay_remove.apply_async([self.image.path], countdown=60*10)
            try:
                super(Face, self).save(*args, **kwargs)
            except: pass


class FaceToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='face_tokens')
    timestamp = models.DateTimeField(default=timezone.now)
    expires = models.DateTimeField(default=timezone.now)
    token = models.CharField(default='', max_length=100)
    length = models.IntegerField(default=6)
    attempts = models.IntegerField(default=0)
    uid = models.CharField(default=uuid.uuid4, max_length=100)
