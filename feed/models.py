from simple_history.models import HistoricalRecords
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.functions import Length
import uuid
import base64, math
from feed.storage import MediaStorage
from django.conf import settings

models.TextField.register_lookup(Length, 'length')

def b64enctxt(txt):
    import base64, math
    txt = txt[:math.floor(200 * 6/8)]
    return base64.urlsafe_b64encode(bytes(txt, 'utf-8')).decode("unicode_escape")

def get_file_path(instance, filename):
    import os
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (str(uuid.uuid4()), ext)
    return os.path.join('files/', filename)

def get_image_path(instance, filename, blur=False, original=False, thumbnail=False):
    import os
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (str(uuid.uuid4()), ext)
    return os.path.join('images/', filename)

def get_auction_end():
    import datetime
    return timezone.now() + datetime.timedelta(hours=24*settings.AUCTION_END_DAYS)

class Post(models.Model):
    id = models.AutoField(primary_key=True)
    feed = models.CharField(max_length=500, default="private")
    uuid = models.TextField(max_length=500, default=uuid.uuid4)
    content = models.TextField(blank=True)
    content_compiled = models.TextField(blank=True)
    date_posted = models.DateTimeField(default=timezone.now)
    date_uploaded = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='post_recipient')
    image = models.ImageField(upload_to=get_image_path, null=True, blank=True, max_length=500)
    image_hash = models.TextField(blank=True)
    image_bucket = models.ImageField(storage=MediaStorage(), upload_to=get_image_path, null=True, blank=True, max_length=500)
    image_original = models.ImageField(upload_to=get_image_path, null=True, blank=True, max_length=500)
    image_original_bucket = models.ImageField(storage=MediaStorage(), upload_to=get_image_path, null=True, blank=True, max_length=500)
    image_censored = models.ImageField(upload_to=get_image_path, null=True, blank=True, max_length=500)
    image_censored_bucket = models.ImageField(storage=MediaStorage(), null=True, blank=True, max_length=500)
    image_censored_thumbnail = models.ImageField(upload_to=get_image_path, null=True, blank=True, max_length=500)
    image_censored_thumbnail_bucket = models.ImageField(storage=MediaStorage(), upload_to=get_image_path, null=True, blank=True, max_length=500)
    image_public = models.ImageField(upload_to=get_image_path, null=True, blank=True, max_length=500)
    image_public_bucket = models.ImageField(storage=MediaStorage(), upload_to=get_image_path, null=True, blank=True, max_length=500)
    image_thumbnail = models.ImageField(upload_to=get_image_path, null=True, blank=True, max_length=500)
    image_thumbnail_bucket = models.ImageField(storage=MediaStorage(), upload_to=get_image_path, null=True, blank=True, max_length=500)
    image_static = models.CharField(max_length=500, null=True, blank=True)
    image_sightengine = models.TextField(blank=True)
    file = models.FileField(upload_to=get_file_path, null=True, blank=True)
    file_bucket = models.FileField(storage=MediaStorage(), null=True, blank=True, max_length=500)
    file_sample = models.FileField(upload_to=get_file_path, null=True, blank=True)
    file_sample_bucket = models.FileField(storage=MediaStorage(), null=True, blank=True, max_length=500)
    file_sightengine = models.TextField(blank=True)
    private = models.BooleanField(default=False)
    public = models.BooleanField(default=False)
    safe = models.BooleanField(default=True)
    pinned = models.BooleanField(default=False)
    rotation = models.IntegerField(default=0)
    price = models.CharField(default='5', max_length=10)
    viewers = models.ManyToManyField(User, related_name='post_view', blank=True)
    enhanced = models.BooleanField(default=False)
    uploaded = models.BooleanField(default=False)
    published = models.BooleanField(default=False)
    posted = models.BooleanField(default=False)
    secure = models.BooleanField(default=False)
    offsite = models.BooleanField(default=False)
    image_offsite = models.CharField(default='', null=True, blank=True, max_length=600)
    image_thumb_offsite = models.CharField(default='', null=True, blank=True, max_length=600)
    confirmation_id = models.TextField(blank=True)
    friendly_name = models.CharField(default='', null=True, blank=True, max_length=512)
    date_auction = models.DateTimeField(default=get_auction_end)
    paid_file = models.BooleanField(default=False)
    paid_users = models.ManyToManyField(User, related_name='paid_posts', blank=True)
    history = HistoricalRecords()

#    def likes(self):
#        return Profile.objects.filter(likes__in=[self]).count()

    def get_web_url(self):
        from django.conf import settings
        return '{}{}/media/images/{}.png'.format('https://', settings.STATIC_DOMAIN, self.uuid)

    def get_web_thumb_url(self):
        from django.conf import settings
        return '{}{}/media/images/{}-thumb.png'.format('https://', settings.STATIC_DOMAIN, self.uuid)

    def copy_web(self, force=False):
        import os, shutil
        from django.conf import settings
        if not self.image: return
        new_path = os.path.join(settings.BASE_DIR, 'web/site/media/images/', '{}{}'.format(self.uuid, '.png'))
        if not os.path.exists(new_path) or force:
            if not os.path.exists(self.image.path): self.download_photo()
            if not os.path.exists(self.image.path): return
            shutil.copy(self.image.path, new_path)
        new_path_thumb = os.path.join(settings.BASE_DIR, 'web/site/media/images/', '{}{}'.format(self.uuid, '-thumb.png'))
        if self.image_thumbnail and (not os.path.exists(new_path_thumb)) or force:
            if not os.path.exists(self.image_thumbnail.path): self.download_thumbnail()
            if not os.path.exists(self.image_thumbnail.path): return
            self.get_image_thumb_url()
            shutil.copy(self.image_thumbnail.path, new_path_thumb)

    def has_auction(self):
        return timezone.now() < self.date_auction

    def compile_content(self):
        from .compile import compile
        compile(self)

    def get_file_sample(self):
        if self.file_sample_bucket: return self.file_sample_bucket.url
        self = self.make_file_sample()
        self.save()
        self = Post.objects.get(id=self.id)
        if self.file_sample_bucket: return self.file_sample_bucket.url
        return None

    def make_file_sample(self):
#        if self.file_sample_bucket: return self.file_sample_bucket.url
        import os
        if not self.file or not os.path.exists(self.file.path): self.download_file()
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(self.file.path)
            ten_seconds = audio[:settings.FREE_AUDIO_MS]
            ten_seconds.export(str(self.file.path) + '.short.mp3', format="mp3")
            self.file_sample = str(self.file.path) + '.short.mp3'
            self.save()
        except: pass
        return self

    def get_image_url(self):
        from django.conf import settings
        import os
        from feed.middleware import get_current_request
        if settings.USE_OFFSITE and self.image_offsite and self.public and (not get_current_request().user.is_authenticated if get_current_request() else True): return self.image_offsite
        if os.path.exists(os.path.join(settings.BASE_DIR, 'web/site/media/images/', '{}.png'.format(self.uuid))): return self.get_web_url()
        if self.image_bucket: return self.image_bucket.url
        from security.secure import get_secure_path, get_private_secure_path, get_secure_video_path
        from feed.models import Post
        from feed.logo import add_logo
        import os, shutil
        path, url = get_private_secure_path(self.image.name)
        full_path = os.path.join(settings.BASE_DIR, path)
        try:
            shutil.copy(self.image.path, full_path)
        except:
            try:
                shutil.copy(self.image_original.path, self.image.path)
                shutil.copy(self.image_original.path, full_path)
            except:
                try:
                    self.download_original()
                    self = Post.objects.get(id=self.id)
                    shutil.copy(self.image_original.path, self.image.path)
                    shutil.copy(self.image_original.path, full_path)
                except:
                    if len(self.content) < 120: self.delete()
                    return '/media/static/default.png'
        from lotteh.celery import remove_secure
        add_logo(full_path)
        remove_secure.apply_async([full_path], countdown=settings.REMOVE_SECURE_TIMEOUT_SECONDS)
        return url

    def get_image_thumb_url(self):
        from django.conf import settings
        from feed.middleware import get_current_request
        from security.secure import get_secure_path, get_private_secure_path, get_secure_video_path
        import os
        if settings.USE_OFFSITE and self.image_thumb_offsite and self.public and not get_current_request().user.is_authenticated if get_current_request() else False: return self.image_thumb_offsite
        if os.path.exists(os.path.join(settings.BASE_DIR, 'web/site/media/images/', '{}-thumb.png'.format(self.uuid))): return self.get_web_thumb_url()
        if self.image_thumbnail_bucket: return self.image_thumbnail_bucket.url
        from security.secure import get_secure_path, get_private_secure_path, get_secure_video_path
        from feed.logo import add_logo
        import os, shutil
        if not self.image_thumbnail or not os.path.exists(self.image_thumbnail.path):
            new_path = os.path.join(settings.BASE_DIR, 'media/', get_image_path(self, self.image.name, blur=True))
            try:
                shutil.copy(self.image.path, new_path)
            except:
                try:
                    shutil.copy(self.image_original.path, self.image.path)
                    shutil.copy(self.image_original.path, new_path)
                except:
                    try:
                        self.download_photo()
                        self = Post.objects.get(id=self.id)
                        shutil.copy(self.image.path, new_path)
                    except:
                        if len(self.content) < 120: self.delete()
                        return '/media/static/default.png'
            resize_image(new_path)
            self.image_thumbnail = new_path
            self.save()
        path, url = get_private_secure_path(self.image_thumbnail.name)
        full_path = os.path.join(settings.BASE_DIR, path)
        shutil.copy(self.image_thumbnail.path, full_path)
        from lotteh.celery import remove_secure
        remove_secure.apply_async([full_path], countdown=settings.REMOVE_SECURE_TIMEOUT_SECONDS)
        return url

    def get_blur_url(self):
        from django.conf import settings
        from feed.middleware import get_current_request
        if settings.USE_OFFSITE and self.image_offsite and not get_current_request().user.is_authenticated if get_current_request() else False: return self.image_offsite
        if self.image_censored_bucket: return self.image_censored_bucket.url
        full_path = None
        url = None
        from security.secure import get_secure_path, get_private_secure_path, get_secure_video_path
        from feed.logo import add_logo
        import os, shutil
        if not self.image_censored or not os.path.exists(self.image_censored.path):
            new_path = os.path.join(settings.BASE_DIR, 'media/', get_image_path(self, self.image.name, blur=True))
            try:
                shutil.copy(self.image.path, new_path)
            except:
                try:
                    shutil.copy(self.image_original.path, self.image.path)
                    shutil.copy(self.image_original.path, new_path)
                except:
                    try:
                        self.download_photo()
                        self = Post.objects.get(id=self.id)
                        shutil.copy(self.image.path, new_path)
                    except:
                        if len(self.content) < 120: self.delete()
                        return '/media/static/default.png'
            resize_image(new_path)
            from .blur import blur_faces, blur_nude
            blur_nude(new_path, new_path)
#            blur_faces(new_path)
            self.image_censored = new_path #.split('media/')[1]
            self.save()
            path, url = get_secure_path(self.image_censored.name)
            full_path = os.path.join(settings.BASE_DIR, path)
            shutil.copy(self.image_censored.path, full_path)
        else:
            path, url = get_secure_path(self.image_censored.name)
            full_path = os.path.join(settings.BASE_DIR, path)
            shutil.copy(self.image_censored.path, full_path)
        from lotteh.celery import remove_secure
        remove_secure.apply_async([full_path], countdown=120)
        return url

    def get_blur_thumb_url(self):
        from django.conf import settings
        from feed.middleware import get_current_request
        if settings.USE_OFFSITE and self.image_thumb_offsite and not get_current_request().user.is_authenticated if get_current_request() else False: return self.image_thumb_offsite
        if self.image_censored_thumbnail_bucket: return self.image_censored_thumbnail_bucket.url
        full_path = None
        from security.secure import get_secure_path, get_private_secure_path, get_secure_video_path
        from feed.models import Post
        from feed.logo import add_logo
        import os, shutil
        if not self.image_censored_thumbnail or not os.path.exists(self.image_censored_thumbnail.path) or not os.path.exists(self.image_censored_thumbnail.path):
            self.get_blur_url()
            new_path = os.path.join(settings.BASE_DIR, 'media/', get_image_path(self, self.image.name, blur=True))
            try:
                shutil.copy(self.image_censored.path, new_path)
                resize_image(new_path)
                self.image_censored_thumbnail = new_path
                self.save()
            except: return self.get_face_blur_thumb_url() #'/media/static/default.png'
        path, url = get_secure_path(self.image_censored_thumbnail.name)
        full_path = os.path.join(settings.BASE_DIR, path)
        shutil.copy(self.image_censored_thumbnail.path, full_path)
        from lotteh.celery import remove_secure
        remove_secure.apply_async([full_path], countdown=120)
        return url

    def get_face_blur_url(self):
        from django.conf import settings
        if self.image_offsite and settings.USE_OFFSITE: return self.image_offsite
        if self.image_public_bucket: return self.image_public.url
        from security.secure import get_secure_path, get_private_secure_path, get_secure_video_path
        from feed.logo import add_logo
        import os, shutil
        path, url = get_secure_path(self.image.name)
        full_path = os.path.join(settings.BASE_DIR, path)
        try:
            shutil.copy(self.image.path, full_path)
        except:
            shutil.copy(self.image_original.path, self.image.path)
            shutil.copy(self.image_original.path, full_path)
            return
        from lotteh.celery import remove_secure
#        blur_faces(full_path)
        remove_secure.apply_async([full_path], countdown=settings.REMOVE_SECURE_BLUR_TIMEOUT_SECONDS)
        return url

    def get_face_blur_thumb_url(self, static=False):
        from django.conf import settings
        from feed.middleware import get_current_request
        if settings.USE_OFFSITE and self.image_thumb_offsite and not get_current_request().user.is_authenticated if get_current_request() else False: return self.image_thumb_offsite
        from django.conf import settings
        from security.secure import get_secure_path, get_private_secure_path, get_secure_video_path
        from feed.logo import add_logo
        import os, shutil
        from retargeting.path import get_email_path
        if self.image_thumbnail_bucket and not static: return self.image_thumbnail_bucket.url
        elif static and self.image_thumbnail_bucket and not self.image_static:
            path, url = get_email_path(self.image_thumbnail_bucket.name)
            with open(path, mode='wb') as write_file:
                with self.image_thumbnail_bucket.storage.open(str(self.image_thumbnail_bucket), mode='rb') as image_file:
                    write_file.write(image_file.read())
            self.image_static = url
            self.save()
            return url
        if not self.image_thumbnail or not os.path.exists(self.image_thumbnail.path):
            new_path = os.path.join(settings.BASE_DIR, 'media/', get_image_path(self, self.image.name, blur=True))
            try:
                shutil.copy(self.image.path, new_path)
            except:
                try:
                    shutil.copy(self.image_original.path, self.image.path)
                    shutil.copy(self.image_original.path, new_path)
                except:
                    try:
                        self.download_photo()
                        self = Post.objects.get(id=self.id)
                        shutil.copy(self.image.path, new_path)
                    except:
                        if len(self.content) < 120: self.delete()
                        return '/media/static/default.png'
            try:
                resize_image(new_path)
                self.image_thumbnail = new_path
                self.save()
            except:
                if len(self.content) < 120: self.delete()
                return '/media/static/default.png'
        path, url = get_secure_path(self.image_thumbnail.name)
        full_path = os.path.join(settings.BASE_DIR, path)
        if not self.public:
            shutil.copy(self.image_thumbnail.path, full_path)
#            blur_faces(full_path)
            from lotteh.celery import remove_secure
            remove_secure.apply_async([full_path], countdown=settings.REMOVE_SECURE_BLUR_TIMEOUT_SECONDS)
        if self.public and (not self.image_public or not os.path.exists(self.image_public.path)):
            shutil.copy(self.image_thumbnail.path, full_path)
#            blur_faces(full_path)
            self.image_public = full_path
            self.save()
        if static and not self.image_static:
            path, url = get_email_path(self.image_thumbnail.name)
            with open(path, mode='wb') as write_file:
                with open(str(self.image_thumbnail.path), mode='rb') as image_file:
                    write_file.write(image_file.read())
            self.image_static = url
            self.save()
            return url
        elif self.image_static: return self.image_static
        return url if not self.public else '/feed/secure/photo/' + str(self.image_public.path).split('/')[-1] #self.image_public.path[len(str(os.path.join(settings.MEDIA_ROOT, '/secure/media/')):]

    def get_file_url(self):
        from django.conf import settings
        if self.file_bucket: return self.file_bucket.url
        import shutil, os
        from security.secure import get_secure_path, get_private_secure_path, get_secure_video_path
        path, url = get_secure_video_path(self.file.name)
        full_path = os.path.join(settings.BASE_DIR, path)
        shutil.copy(self.file.path, full_path)
        from lotteh.celery import remove_secure
        remove_secure.apply_async([full_path], countdown=settings.REMOVE_SECURE_TIMEOUT_FILE_SECONDS)
        return reverse('live:stream-secure-video', kwargs={'filename': url})

    def user_likes(self):
        from feed.middleware import get_current_user
        return get_current_user() in self.likes.all()

    def get_likes(self):
        likes = []
        count = 0
        for like in self.likes.all():
            likes[count] = like.username
            count = count + 1
        return likes

    def number_of_likes(self):
        return self.likes.count()

    def get_absolute_url(self):
        from django.urls import reverse
        if self.friendly_name: return reverse('feed:post-detail', kwargs={'uuid': self.friendly_name})
        else: return self.get_friendly_name()

    def get_friendly_name(self, save=True):
        from django.utils.html import strip_tags
        from feed.templatetags.app_filters import clean_html
        content = strip_tags(clean_html(self.content)).split('\n')[0]
        #if self.friendly_name and not self.content: reverse('feed:post-detail', kwargs={'uuid': self.friendly_name})
        import urllib.parse
        name = urllib.parse.quote_plus(((content[:content.rfind(' ', 20, 32) if content.rfind(' ', 20, 32) else 32].strip() if content else 'post').replace(' ', '-').replace('"', '').replace('\'', '').replace('?', '').replace('\\', '').replace('/', '').replace(',', '')).lower()[:255])[:100]
        import random, os, urllib
        from django.conf import settings
        from django.urls import reverse
        if Post.objects.filter(friendly_name=name).count() == 0:
            self.friendly_name = name
            if save: self.save()
            return reverse('feed:post-detail', kwargs={'uuid': name})
        words = 0
        import random
        if self.image: random.seed(self.image_hash)
        while words < 100:
            ex = ''
            with open(os.path.join(settings.BASE_DIR, 'feed/common_words.txt'), 'r') as file:
                lines = file.readlines()
                for x in range(settings.POST_WORDS + words):
                    ex = ex + ' {}'.format(random.choice(lines)[:-1])
            name = urllib.parse.quote_plus((((content.split('\n')[0][:content.rfind(' ', 20, 32) if content.rfind(' ', 20, 32) else 32].strip() if content else 'post') + ex).replace(' ', '-')).lower()[:255])[:100]
            file.close()
            if Post.objects.filter(friendly_name=name).count() == 0: break
            words = words + 1
        self.friendly_name = name
        if save: self.save()
        return reverse('feed:post-detail', kwargs={'uuid': name})

    def clear_censor(self):
        import os
        if self.image_censored or self.image_thumbnail:
            try:
                os.remove(self.image_thumbnail.path)
            except: pass
            try:
                os.remove(self.image_censored.path)
            except: pass
            try:
                os.remove(self.image_public.path)
            except: pass
            if self.image_censored_thumbnail:
                try:
                    os.remove(self.image_censored_thumbnail.path)
                except: pass
            self.image_censored = None
            self.image_thumbnail = None
            self.image_censored_thumbnail = None
            self.image_censored_bucket = None
            self.image_thumbnail_bucket = None
            self.image_censored_thumbnail_bucket = None
            self.image_public_bucket = None
            self.save()

    def rotate_align(self):
 #       import PIL
 #       PIL.Image.MAX_IMAGE_PIXELS = 93312000000
        from PIL import Image
        self.download_photo()
        from .align import face_angle_detect
        angle = face_angle_detect(self.image.path)
        img = Image.open(self.image.path)
        img = img.rotate(-angle,expand=0)
        img.save(self.image.path)
        self.rotation = self.rotation + 1
        self.clear_censor()
        self.upload()
        self.save()

    def rotate_right(self):
        self.download_photo()
        rotate(self.image.path, 1)
        self.rotation = self.rotation + 1
        self.clear_censor()
        self.upload()
        self.save()

    def rotate_flip(self):
        self.download_photo()
        from .rotate import rotate
        rotate(self.image.path, 2)
        self.rotation = self.rotation + 1
        self.clear_censor()
        self.upload()
        self.save()

    def rotate_left(self):
        self.download_photo()
        from .rotate import rotate
        rotate(self.image.path, -1)
        self.rotation = self.rotation + 1
        self.clear_censor()
        self.upload()
        self.save()

    def download_photo(self):
        import os
        from django.conf import settings
        try:
            if self.image and os.path.exists(self.image.path): return
        except: pass
        with self.image_bucket.storage.open(str(self.image_bucket), mode='rb') as bucket_file:
            full_path = os.path.join(settings.BASE_DIR, 'media/', get_image_path(self, 'image.png'))
            with open(full_path, "wb") as image_file:
                image_file.write(bucket_file.read())
            image_file.close()
            self.image = full_path
            self.save()
        bucket_file.close()

    def download_thumbnail(self):
        import os
        from django.conf import settings
        try:
            if self.image_thumbnail and os.path.exists(self.image_thumbnail.path): return
        except: pass
        with self.image_thumbnail_bucket.storage.open(str(self.image_thumbnail_bucket), mode='rb') as bucket_file:
            full_path = os.path.join(settings.BASE_DIR, 'media/', get_image_path(self, 'image.png'))
            with open(full_path, "wb") as image_file:
                image_file.write(bucket_file.read())
            image_file.close()
            self.image_thumbnail = full_path
            self.save()
        bucket_file.close()

    def download_file(self):
        import os
        from django.conf import settings
        try:
            if self.file and os.path.exists(self.file.path): return
        except: pass
        with self.file_bucket.storage.open(str(self.file_bucket), mode='rb') as bucket_file:
            full_path = os.path.join(settings.BASE_DIR, 'media/', get_file_path(self, self.file_bucket.name))
            with open(full_path, "wb") as image_file:
                image_file.write(bucket_file.read())
            image_file.close()
            self.file = full_path
            self.save()
        bucket_file.close()

    def download_original(self):
        import os
        from django.conf import settings
        try:
            if self.image_original and os.path.exists(self.image_original.path): return
        except: pass
        with self.image_original_bucket.storage.open(str(self.image_original_bucket), mode='rb') as bucket_file:
            full_path = os.path.join(settings.BASE_DIR, 'media/', get_image_path(self, 'image.png'))
            with open(full_path, "wb") as image_file:
                image_file.write(bucket_file.read())
            image_file.close()
            self.image_original = full_path
            self.save()
        bucket_file.close()

    def upload(self):
        from enhance.image import bucket_post
        bucket_post(self.id)

    def short_time(self):
        from django.utils import timezone
        from django.conf import settings
        import pytz
        return self.date_posted.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%H:%M:%S')

    def save(self, *args, **kwargs):
#        import PIL
#        PIL.Image.MAX_IMAGE_PIXELS = 93312000000
        from PIL import Image
        from feed.nude import is_nude, is_nude_video
        from django.conf import settings
        import os, shutil
        this = None
        try:
            from feed.text import is_safe_text, censor
            if not is_safe_text(self.content):
                if len(self.content) > settings.POST_READER_LENGTH: self.content = censor(self.content)
                else: self.public = False
            this = Post.objects.filter(id=self.id).first()
            super(Post, self).save(*args, **kwargs)
            if (not this or this.private != self.private or this.public != self.public or this.image != self.image):
                if self.image:
                    full_path = os.path.join(settings.BASE_DIR, 'media/', get_image_path(self, self.image.name))
                    shutil.copy(self.image.path, full_path)
                    os.remove(self.image.path)
                    self.image = full_path
                    img = Image.open(full_path)
                    full_path = str(full_path) + '.png'
                    img.save(full_path, 'PNG')
                    os.remove(self.image.path)
                    self.image = full_path
                if self.file:
                    full_path = os.path.join(settings.BASE_DIR, 'media/', get_file_path(self, self.file.name))
                    shutil.copy(self.file.path, full_path)
                    os.remove(self.file.path)
                    self.file = full_path
            if this and this.image != self.image:
                os.remove(this.image.path)
                os.remove(this.image_original.path)
                os.remove(this.image_censored.path)
                os.remove(this.image_thumbnail.path)
                os.remove(this.image_censored_thumbnail.path)
                self.image_original = None
                self.image_censored = None
                self.image_censored_thumbnail = None
                self.image_thumbnail = None
                self.image_offsite = ''
                self.image_thumb_offsite = ''
                self.uploaded = False
                self.enhanced = False
                self.offsite = False
                censor_image(self.image.path)
            if self.image and (not this or this.private != self.private or this.image != self.image):
                from .apis import is_safe_public_image, is_safe_private_image, sightengine_image, sightengine_file
                safe = False
                if self.private:
#                    self.image_sightengine = sightengine_image(self.file.path)
                    pass
                if self.public or settings.NUDITY_FILTER:
                    self.published = False
#                    safe = is_safe_public_image(self.image.path)
#                else:
#                    safe = is_safe_private_image(self.image.path)
#                if not safe and self.public:
#                    os.remove(self.image.path)
#                    self.image = None
#                else:
#                    safe = is_safe_private_image(self.image.path)
#                    if not safe:
#                        os.remove(self.image.path)
#                        self.image = None
            if this and this.file != self.file:
                os.remove(this.file.path)
            if self.file and (not this or this.private != self.private or this.file != self.file):
                if self.public or settings.NUDITY_FILTER:
                    if is_nude_video(self.file.path):
                        self.public = False
                        if settings.NUDITY_FILTER:
                            os.remove(self.file.path)
                            self.file = None
#                safe = None
#                if self.private:
#                    self.file_sightengine = sightengine_file(self.file.path)
#                    pass
#                if self.public:
#                    safe = is_safe_public_video(self.file.path)
#                else:
#                    safe = is_safe_private_video(self.file.path)
#                if not safe and self.public:
#                    os.remove(self.file.path)
#                    self.file = None
#                else:
#                    safe = is_safe_private_video(self.file.path)
#                    if not safe:
#                        os.remove(self.file.path)
#                        self.file = None
        except: pass

        if self.image and not self.image_thumbnail and os.path.exists(self.image.path) and self.image.name != 'static/default.png':
            path = os.path.join(settings.BASE_DIR, 'media/', get_image_path(self, self.image.name, blur=False, original=False, thumbnail=True))
            full_path = path
            shutil.copy(self.image.path, full_path)
            self.image_thumbnail = full_path
            img = Image.open(self.image_thumbnail.path)
            if img:
                if img.height > settings.THUMB_IMAGE_DIMENSION or img.width > settings.THUMB_IMAGE_DIMENSION:
                    output_size = (settings.THUMB_IMAGE_DIMENSION, settings.THUMB_IMAGE_DIMENSION)
                    max = img.width
                    if img.height < img.width:
                        max = img.height
                    from feed.crop import crop_center
                    img = crop_center(img,max,max)
                    if img:
                        img.save(self.image_thumbnail.path)
                        img = Image.open(self.image_thumbnail.path)
                        img.thumbnail(output_size)
                        img.save(self.image_thumbnail.path)
        if self.image and not self.image_original and self.image.name != 'static/default.png':
            path = os.path.join(settings.BASE_DIR, 'media/', get_image_path(self, self.image.name, blur=False, original=True))
            full_path = path
            try:
                shutil.copy(self.image.path, full_path)
                self.image_original = full_path
            except: self.image = None
        if self.image and os.path.exists(self.image.path) and self.image.name != 'static/default.png':
            img = Image.open(self.image.path)
            if img.height > settings.MAX_IMAGE_DIMENSION or img.width > settings.MAX_IMAGE_DIMENSION:
                output_size = (settings.MAX_IMAGE_DIMENSION, settings.MAX_IMAGE_DIMENSION)
                max = img.width
                if img.height < img.width:
                    max = img.height
                from feed.crop import crop_center
                img = crop_center(img,max,max)
                if img:
                    img.save(self.image.path)
                    img.thumbnail(output_size)
                    img = Image.open(self.image.path)
                    img.save(self.image.path)
        if self.file and (self.file and ((not self.file_bucket) or self.file.path != this.file.path)):
            towrite = self.file_bucket.storage.open(self.file.path, mode='wb')
            with self.file.open('rb') as file:
                towrite.write(file.read())
            towrite.close()
            self.file_bucket = self.file.path
            self.file_sample_bucket = None
            self = self.make_file_sample()
            self.file_sample = self.file.path
            towrite = self.file_sample_bucket.storage.open(self.file_sample.path, mode='wb')
            with self.file.open('rb') as file:
                towrite.write(file.read())
            towrite.close()
            self.file_sample_bucket = self.file_sample.path
        if not settings.FIX_CONTENT and self and self.image_original and ((this and self.image_original != this.image_original and self.image_original) or (not self.image_hash and self.image_original and os.path.exists(self.image_original.path))) and self.image_original.name != 'static/default.png':
            import hashlib
            with open(self.image_original.path, 'rb') as f:
                self.image_hash = hashlib.md5(f.read()).hexdigest()
        if self.content == '' and not self.image and not self.file and not self.image_bucket and not self.file_bucket:
            self.private = True
        if (not this or this.private != self.private or this.public != self.public or this.image != self.image) and self.image:
            from lotteh.celery import upload_post
            upload_post.delay(self.id)
        if (not this or (this.content != self.content)): # and self.content and len(self.content) > 32:
            self.friendly_name = ''
            self.get_friendly_name(save=False)
        if (this and this.content != self.content or not this) and len(self.content) > 500 and '***' in self.content and self.posted:
            from lotteh.celery import write_post_book
            write_post_book.delay(self.id)
        try:
            super(Post, self).save(*args, **kwargs)
        except: pass

    def delete(self):
        if self.image:
            try:
                os.remove(self.image.path)
            except: pass
            try:
                os.remove(self.image_thumbnail.path)
            except: pass
            try:
                os.remove(self.image_censored.path)
            except: pass
            try:
                os.remove(self.image_censored_thumbnail.path)
            except: pass
            try:
                os.remove(self.image_public.path)
            except: pass
            try:
                os.remove(self.image_original.path)
            except: pass
        if self.file:
            try:
                os.remove(self.file.path)
            except: pass
        try:
            super(Post, self).delete()
        except: pass

def resize_image(image_path):
#    import PIL
#    PIL.Image.MAX_IMAGE_PIXELS = 93312000000
    from PIL import Image
    img = Image.open(image_path)
    output_size = (settings.MAX_RED_IMAGE_DIMENSION, settings.MAX_RED_IMAGE_DIMENSION)
    max = img.width
    if img.height < img.width:
        max = img.height
    from feed.crop import crop_center
    img = crop_center(img,max,max)
    img.save(image_path)
    img = Image.open(image_path)
    img.thumbnail(output_size)
    img.save(image_path)

class Report(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports', null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reports', null=True, blank=True)
    text = models.TextField(default='', null=True, blank=True)

class Bid(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids', null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bids', null=True, blank=True)
    bid = models.IntegerField(default=settings.MIN_BID)
