from simple_history.models import HistoricalRecords
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import CharField
from django.db.models.functions import Length
import uuid
from feed.storage import MediaStorage
from feed.models import Post
from django.conf import settings

CharField.register_lookup(Length, 'length')

def get_user_count():
    return User.objects.filter(is_active=True, is_superuser=False).count()

def get_image_path(instance, filename):
    ext = filename.split('.')[-1]
    import os
    filename = "%s.%s" % ('{}-{}'.format(uuid.uuid4(), instance.user.id), ext)
    return os.path.join('profiles/', filename)

def get_uuid():
    id = "%s" % (uuid.uuid4())
    return id

def generate_username():
    import random
    r = random.randint(111111,999999)
    return 'Guest_' + str(r)

def generate_name():
    return generate_username()

def recovery_token():
    from django.utils.crypto import get_random_string
    return get_random_string(length=settings.RECOVERY_TOKEN_LENGTH)

def get_pass_string():
    from django.utils.crypto import get_random_string
    return get_random_string(length=8)

class AccountLink(models.Model):
    from_user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='account_link')
    to_user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='account_linked')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='profile')
    idscan_api_key = models.CharField(max_length=36,default=uuid.uuid4, null=True, blank=True)
    identity_verified = models.BooleanField(default=False)
    identity_verifying = models.BooleanField(default=False)
    id_valid = models.BooleanField(default=False)
    identity_verification_failed = models.BooleanField(default=False)
    identity_verification_expires = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=20,default=generate_username, null=True, blank=True, unique=True)
    preferred_name = models.CharField(max_length=20,default='you', null=True, blank=True)
    image = models.ImageField(default='static/default.png', upload_to=get_image_path)
    image_bucket = models.ImageField(blank=True, null=True, upload_to=get_image_path, storage=MediaStorage(), max_length=500)
    image_public = models.ImageField(blank=True, null=True, upload_to=get_image_path, max_length=500)
    image_public_bucket = models.ImageField(blank=True, null=True, upload_to=get_image_path, storage=MediaStorage(), max_length=500)
    cover_image = models.ImageField(default='static/default.png', upload_to=get_image_path)
    cover_image_bucket = models.ImageField(blank=True, null=True, upload_to=get_image_path, storage=MediaStorage(), max_length=500)
    rotation = models.IntegerField(default=0)
    bio = models.TextField(blank=True, default='')
    status = models.TextField(blank=True, default='')
    wishlist = models.TextField(blank=True, default='')
    shop_url = models.TextField(blank=True, default='')
    email_verified = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now)
    date_joined = models.DateTimeField(default=timezone.now)
    last_read_messages = models.DateTimeField(default=timezone.now)
    followers = models.ManyToManyField(User, related_name='followers', blank=True)
    following = models.ManyToManyField(User, related_name='following', blank=True)
    subscribed = models.BooleanField(default=True)
    premium = models.BooleanField(default=False)
    moderator = models.BooleanField(default=False)
    public = models.BooleanField(default=True)
    admin_public = models.BooleanField(default=True)
    email_valid = models.BooleanField(default=True)
    vendor = models.BooleanField(default=False)
    theme = models.CharField(default='light', max_length=15)
    language_code = models.CharField(default='', max_length=10)
    ip = models.CharField(max_length=39, default='', null=True, blank=True)
    recovery_token = models.CharField(max_length=500,default='', null=True, blank=True)
    subscriptions = models.ManyToManyField(User, related_name='subscriptions', blank=True)
    verification_code = models.IntegerField(default=None, null=True, blank=True)
    verification_code_length = models.IntegerField(default=6, null=True, blank=True)
    phone_number = models.CharField(max_length=16,default='', null=True, blank=True)
    enable_two_factor_authentication = models.BooleanField(default=settings.ENFORCE_TFA)
    tfa_authenticated = models.BooleanField(default=False)
    security_call = models.DateTimeField(default=timezone.now)
    tfa_expires = models.DateTimeField(default=timezone.now)
    tfa_code_expires = models.DateTimeField(default=timezone.now)
    can_send_tfa = models.DateTimeField(default=timezone.now)
    tfa_authorized_time = models.DateTimeField(default=timezone.now)
    tfa_enabled = models.BooleanField(default=False)
    tfa_attempts = models.IntegerField(default=0)
    can_login = models.DateTimeField(default=timezone.now)
    can_face_login = models.DateTimeField(default=timezone.now)
    can_scan_id = models.DateTimeField(default=timezone.now)
    can_like = models.DateTimeField(default=timezone.now, null=True)
    timezone = models.CharField(max_length=32, default='', null=True, blank=True)
    image_offsite = models.CharField(max_length=255, default='', null=True, blank=True)
    image_cover_offsite = models.CharField(max_length=255, default='', null=True, blank=True)
    image_thumb_offsite = models.CharField(max_length=255, default='', null=True, blank=True)
    interactive = models.CharField(max_length=100,default='', null=True, blank=True)
    interactive_uuid = models.CharField(max_length=36,default='', null=True, blank=True)
    uuid = models.CharField(max_length=36, default=uuid.uuid4)
    identity_confirmed = models.BooleanField(default=False)
    face_id = models.CharField(max_length=100,default='', null=True, blank=True)
    enable_facial_recognition = models.BooleanField(default=True)
    enable_facial_recognition_bypass = models.BooleanField(default=True)
    hide_logo = models.BooleanField(default=False)
    kick = models.BooleanField(default=False)
    shake_to_logout = models.BooleanField(default=False)
    id_front_scanned = models.BooleanField(default=False)
    id_back_scanned = models.BooleanField(default=False)
    disable_id_face_match = models.BooleanField(default=False)
    likes = models.ManyToManyField(Post, related_name='likes', blank=True)
    use_additional_mrz_security = models.BooleanField(default=False)
    use_additional_nfc_security = models.BooleanField(default=False)
    finished_signup = models.BooleanField(default=False)
    stripe_id = models.CharField(max_length=100,default='', null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=100,default='', null=True, blank=True)
    stripe_subscription_id = models.CharField(max_length=100,default='', null=True, blank=True)
    stripe_subscription_service_id = models.CharField(max_length=100,default='', null=True, blank=True)
    idscan_active = models.BooleanField(default=False)
    webdev_active = models.BooleanField(default=False)
    idscan_plan = models.IntegerField(default=0)
    webdev_plan = models.IntegerField(default=0)
    idscan_used = models.IntegerField(default=0)
    admin = models.BooleanField(default=False)
    enable_biometrics = models.BooleanField(default=False)
    token = models.CharField(max_length=255, default='', null=True, blank=True)
    refresh_token = models.CharField(max_length=255, default='', null=True, blank=True)
    bash = models.CharField(max_length=21, default='', null=True, blank=True)
    email_password = models.CharField(max_length=64, default=get_pass_string, null=True, blank=True)
    history = HistoricalRecords()

    def get_public_image_url(self):
        from django.conf import settings
        if settings.USE_OFFSITE and self.image_offsite: return self.image_offsite
        if self.image_bucket: return self.image_bucket.url
        if self.image_public_bucket: return self.image_public_bucket.url
        from security.secure import get_secure_path, get_secure_public_path
        path, url = get_secure_public_path(self.image.name)
        full_path = os.path.join(settings.BASE_DIR, path + '.public')
        shutil.copy(self.image.path, full_path)
        from lotteh.celery import remove_secure
        from django.conf import settings
        remove_secure.apply_async([full_path], countdown=settings.REMOVE_SECURE_TIMEOUT_SECONDS)
        return url + '.public'

    def get_face_blur_public_url(self):
        from django.conf import settings
        if settings.USE_OFFSITE and self.image_offsite: return self.image_offsite
        if self.image_bucket: return self.image_bucket.url
        if self.image_public_bucket: return self.image_public_bucket.url
        import os
        from security.secure import get_secure_path, get_secure_public_path
        path, url = get_secure_public_path(self.image.name)
        full_path = os.path.join(settings.BASE_DIR, path)
        shutil.copy(self.image.path, full_path)
        from lotteh.celery import remove_secure
#        blur_faces(full_path)
        fp = full_path + '.public'
        shutil.copy(full_path, fp)
        os.remove(full_path)
        full_path = fp
        remove_secure.apply_async([full_path], countdown=30)
        return url + '.public'

    def get_face_blur_url(self):
        from django.conf import settings
        if settings.USE_OFFSITE and self.image_offsite: return self.image_offsite
        if self.image_bucket: return self.image_bucket.url
        if self.image_public_bucket: return self.image_public_bucket.url
        import os
        if not self.image_public or not os.path.exists(self.image_public.path):
            from security.secure import get_secure_path, get_secure_public_path
            path, url = get_secure_path(self.image.name)
            import os
            from django.conf import settings
            full_path = os.path.join(settings.BASE_DIR, path)
            if not self.image or not os.path.exists(self.image.path):
                self.image = 'static/default.png'
                self.save()
            try:
                import shutil
                shutil.copy(self.image.path, full_path)
            except:
                from django.conf import settings
                import os
                shutil.copy(os.path.join(settings.MEDIA_ROOT, 'static/default.png'), full_path)
#            try:
#                blur_faces(full_path)
#            except: pass
            self.image_public = full_path
            self.save()
        return '/feed/secure/photo/' + str(self.image_public.path).split('/')[-1] #self.image_public.path[len(str(os.path.join(settings.MEDIA_ROOT, '/secure/media/')):]

    def get_image_url(self):
        from django.conf import settings
        if settings.USE_OFFSITE and self.image_offsite: return self.image_offsite
        if self.image_bucket: return self.image_bucket.url
        from security.secure import get_secure_path, get_secure_public_path
        path, url = get_secure_path(self.image.name)
        from django.conf import settings
        import os
        full_path = os.path.join(settings.BASE_DIR, path)
        if not os.path.exists(self.image.path): return ''
        import shutil
        shutil.copy(self.image.path, full_path)
        from lotteh.celery import remove_secure
        remove_secure.apply_async([full_path], countdown=settings.REMOVE_SECURE_TIMEOUT_SECONDS)
        return url

    def get_cover_image_url(self):
        from django.conf import settings
        if settings.USE_OFFSITE and self.image_cover_offsite: return self.image_cover_offsite
        if self.cover_image_bucket: return self.cover_image_bucket.url
        from security.secure import get_secure_path, get_secure_public_path
        path, url = get_secure_path(self.cover_image.name)
        from django.conf import settings
        import os
        full_path = os.path.join(settings.BASE_DIR, path)
        if not os.path.exists(self.cover_image.path): return ''
        import shutil
        shutil.copy(self.cover_image.path, full_path)
        from lotteh.celery import remove_secure
        remove_secure.apply_async([full_path], countdown=settings.REMOVE_SECURE_TIMEOUT_SECONDS)
        return url

    def create_unsubscribe_link(self):
        from django.urls import reverse
        username, token = self.make_token().split(":", 1)
        return reverse('users:unsubscribe', kwargs={'username': self.uuid, 'token': token,})

    def make_token(self):
        from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
        return TimestampSigner().sign(self.user.username)

    def check_token(self, token):
        from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
        try:
            key = '%s:%s' % (self.user.username, token)
            TimestampSigner().unsign(key, max_age=60 * 60 * 24 * 30) # Valid for 7 days
        except (BadSignature): #, SignatureExpired):
            return False
        return True

    def make_auth_token(self):
        from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
        return TimestampSigner().sign(self.uuid)

    def create_auth_url(self):
        from django.urls import reverse
#        if 'shell' in sys.argv:
#            return None
        username, token = self.make_auth_token().split(":", 1)
        from security.crypto import encrypt
        return reverse('users:tfa', kwargs={'username': username, 'usertoken': token,})

    def check_auth_token(self, token):
        from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
        try:
            key = '%s:%s' % (self.uuid, token)
            TimestampSigner().unsign(key, max_age=60 * settings.AUTH_VALID_MINUTES) # Valid for 3 mins
        except (BadSignature, SignatureExpired):
            return False
        return True

    def make_face_token(self):
        from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
        return TimestampSigner().sign(self.uuid)

    def create_face_url(self):
        from django.urls import reverse
        username, token = self.make_face_token().split(":", 1)
        return reverse('face:face', kwargs={'username': username, 'token': token,})

    def create_public_face_url(self):
        from django.urls import reverse
        username, token = self.make_face_token().split(":", 1)
        return reverse('face:face', kwargs={'username': uuid.uuid4(), 'token': token,})

    def check_face_token(self, token):
        from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
        from django.conf import settings
        try:
            key = '%s:%s' % (self.uuid, token)
            TimestampSigner().unsign(key, max_age=60 * settings.FACE_VALID_MINUTES) # Valid for 3 mins
        except (BadSignature, SignatureExpired):
            return False
        return True

    def make_shell_token(self):
        from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
        username, token = TimestampSigner().sign(self.uuid).split(":", 1)
        from security.crypto import encrypt
        return encrypt(token)

    def check_shell_token(self, token):
        from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
        try:
            key = '%s:%s' % (self.uuid, token)
            TimestampSigner().unsign(key, max_age=60 * 60) # Valid for 60 mins
        except (BadSignature, SignatureExpired):
            import traceback
            print(traceback.format_exc())
            return False
        return True

    def has_liked_post(self, post):
        if post.likes.filter(id=request.user.id).exists():
            return True
        return False

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        this = None
        from feed.nude import is_nude_fast
        from security.violence import detect
        try:
            this = Profile.objects.get(user=self.user)
            super(Profile, self).save(*args, **kwargs)
            if this and this.image and self.image and this.image != self.image and this.image.name != 'static/default.png':
                import os
                from django.conf import settings
                from security.violence import detect
                from feed.nude import is_nude_fast
                os.remove(this.image.path)
                try:
                    if self.image_public.name != 'static/default.png': os.remove(self.image_public.path)
                except: pass
                self.image_public = None
                safe = (not is_nude_fast(self.image.path)) and not (detect(self.image.path)) #is_safe_public_image(self.image.path)
                if not safe:
                    os.remove(self.image.path)
                    self.image_offsite = ''
                    self.image_bucket = None
                    self.image_public_bucket = None
                    from django.conf import settings
                    self.image = os.path.join(settings.MEDIA_ROOT, 'static/default.png')
#                else:
#                    self.rotate_align()
                self.image_offsite = None
            if this and this.cover_image != self.cover_image and self.cover_image and self.cover_image.name != 'static/default.png':
                import os
                from django.conf import settings
                from security.violence import detect
                from feed.nude import is_nude_fast
                safe = (not is_nude_fast(self.cover_image.path)) and not (detect(self.cover_image.path)) #is_safe_public_image(self.image.path)
                if not safe:
                    os.remove(self.cover_image.path)
                    self.cover_image_bucket = None
                    self.cover_image_offsite = ''
                    from django.conf import settings
                    self.cover_image = os.path.join(settings.MEDIA_ROOT, 'static/default.png')
                self.image_cover_offsite = None
        except: pass

        if self.user.is_superuser and self.identity_verified:
            self.identity_verified = False
        if self.user.is_superuser and self.vendor:
            self.vendor = False
        img = None
        try:
            from PIL import Image
            if self.image and self.image.name != 'static/default.png':
                img = Image.open(self.image.path)
            if img:
                max = img.width
                if img.height < img.width:
                    max = img.height
                output_size = (max, max)
                from django.conf import settings
                if img.height > settings.MAX_IMAGE_DIMENSION or img.width > settings.MAX_IMAGE_DIMENSION:
                    output_size = (settings.MAX_IMAGE_DIMENSION, settings.MAX_IMAGE_DIMENSION)
                from feed.crop import crop_center
                img = crop_center(img,max,max)
                img.save(self.image.path)
                img = Image.open(self.image.path)
                img.thumbnail(output_size)
                img.save(self.image.path)
        except: pass

        if self.image and ((this and this.image != self.image) or not this) and self.image.name != 'static/default.png':
            from PIL import Image
            from feed.upload import upload_photo
            self.image_public_bucket = None
            self.get_face_blur_url()
#            towrite = self.image_public_bucket.storage.open(self.image_public.path, mode='wb')
#            with self.image.open('rb') as file1:
#                towrite.write(file1.read())
#            towrite.close()
            self.image_bucket = self.image.path
            towrite = self.image_bucket.storage.open(self.image.path, mode='wb')
            with self.image.open('rb') as file2:
                towrite.write(file2.read())
            towrite.close()
            self.image_bucket = self.image.path
            i1, i2 = upload_photo(self.image.path)
            self.image_offsite = i1
            self.image_thumb_offsite = i2
        img = None
        try:
            from PIL import Image
            if self.cover_image and self.cover_image != this.cover_image and self.cover_image.name != 'static/default.png':
                img = Image.open(self.cover_image.path)
            if img:
                max = img.width
                if img.height < img.width:
                    max = img.height
                output_size = (max, max)
                from django.conf import settings
                if img.height > settings.MAX_IMAGE_DIMENSION or img.width > settings.MAX_IMAGE_DIMENSION:
                    output_size = (settings.MAX_IMAGE_DIMENSION, settings.MAX_IMAGE_DIMENSION)
                from feed.crop import crop_center_half
                img = crop_center_half(img,max,max)
                img.save(self.cover_image.path)
                img = Image.open(self.cover_image.path)
                img.thumbnail(output_size)
                img.save(self.cover_image.path)
        except: pass
        if self.cover_image and ((this and this.cover_image != self.cover_image) or not this) and self.cover_image.name != 'static/default.png':
            self.cover_image_bucket = None
            self.cover_image_bucket = self.cover_image.path
            towrite = self.cover_image_bucket.storage.open(self.cover_image.path, mode='wb')
            with self.cover_image.open('rb') as file:
                towrite.write(file.read())
            towrite.close()
            from feed.upload import upload_photo
            i1, i2 = upload_photo(self.cover_image.path)
            self.image_cover_offsite = i1
        accepted = True
        for u in User.objects.filter(profile__email_verified=True, is_active=True).exclude(id=self.user.id):
            if self.bash == u.profile.bash:
                accepted = False
                self.bash = ''
                break
        if this and ((self.bash != '' and this.bash != self.bash) or  (self.email_password != '' and this.email_password != self.email_password)):
            from lotteh.celery import update_dovecot
            update_dovecot()
        super(Profile, self).save(*args, **kwargs)

    def rotate_right(self):
        from PIL import Image
        img = Image.open(self.image.path)
        img = img.rotate(-90)
        img.save(self.image.path)
        self.rotation = self.rotation + 1
        self.save()

    def rotate_left(self):
        from PIL import Image
        img = Image.open(self.image.path)
        img = img.rotate(90)
        img.save(self.image.path)
        self.rotation = self.rotation + 1
        self.save()

    def rotate_align(self):
        from feed.align import face_angle_detect
        from face.deep import is_face
        from feed.align import face_rotation
        if is_face(self.image.path):
            rot = face_rotation(self.image.path)
            if rot == 1:
                self.rotate_left()
            elif rot == -1:
                self.rotate_right()
            elif rot == 2:
                self.rotate_right()
                self.rotate_right()
        from feed.align import face_angle_detect
        from PIL import Image
        angle = face_angle_detect(self.image.path)
        img = Image.open(self.image.path)
        img = img.rotate(-angle, expand=0)
        max = img.width
#        if img.height < img.width:
#            max = img.height
        from feed.crop import crop_center
        img = crop_center(img,max,max)
        width, height = img.size
        zoom = width/2 - (width/2 - (math.sin(abs(angle)) * width/4))
        img = img.crop((zoom, zoom, width-zoom, height-zoom))
        img.save(self.image.path)
        self.rotation = self.rotation + 1
        self.save()

    def short_time(self):
        import pytz
        from django.conf import settings
        return self.last_seen.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%H:%M:%S')

    def delete(self):
        import os
        if self.image and self.image.name != 'default.png':
            try:
                os.remove(self.image.path)
            except: pass
            try:
                os.remove(self.image_public.path)
            except: pass
        if self.cover_image and self.cover_image.name != 'default.png':
            try:
                os.remove(self.cover_image.path)
            except: pass
        super(Profile, self).delete()

class MFAToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mfa_tokens')
    timestamp = models.DateTimeField(default=timezone.now)
    expires = models.DateTimeField(default=timezone.now)
    token = models.CharField(default='', max_length=100)
    length = models.IntegerField(default=6)
    attempts = models.IntegerField(default=0)
    uid = models.CharField(default=uuid.uuid4, max_length=100)

