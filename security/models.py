from simple_history.models import HistoricalRecords
from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.utils import timezone
from django.urls import reverse
import pytz, uuid, os, shutil
from django.conf import settings
from feed.middleware import get_current_user
from security.secure import get_secure_path, get_private_secure_path
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
from django.db.models.signals import post_save
from django.dispatch import receiver

def get_document_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % ('{}-{}-{}'.format(uuid.uuid4(), instance.timestamp.strftime("%Y%m%d-%H%M%S"), get_current_user().id if get_current_user() else '0'), ext)
    return os.path.join('security/', filename)

class Credential(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='credentials')
    sign_count=models.IntegerField(default=0)
    bin_id = models.BinaryField()
    public_key = models.BinaryField()
    transports = models.TextField(default='')
    name = models.CharField(default='', null=True, blank=True, max_length=100)
    history = HistoricalRecords()

class UserLogin(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_logins')
    timestamp = models.DateTimeField(default=timezone.now)
    history = HistoricalRecords()

class UserSession(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_sessions')
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.CharField(max_length=36, default='')
    session_key = models.CharField(max_length=36, default='', null=True, blank=True)
    user_agent = models.CharField(max_length=200, default='')
    authorized = models.BooleanField(default=False)
    bypass = models.BooleanField(default=False)
    history = HistoricalRecords()

from django.contrib.auth.signals import user_logged_in

def user_logged_in_handler(sender, request, user, **kwargs):
    from users.models import AccountLink
    from security.models import SecurityProfile
    link = AccountLink.objects.filter(from_user=user).first()
    if link:
        logout(request)
        auth_login(request, link.to_user, backend='django.contrib.auth.backends.ModelBackend')
        user = link.to_user
    UserSession.objects.get_or_create(user=user, session_key=request.session.session_key, user_agent=request.META["HTTP_USER_AGENT"], authorized=False)
    if request.user.is_authenticated and not hasattr(request.user, 'security_profile') and isinstance(request.user, User):
        security_profile = SecurityProfile()
        security_profile.user = request.user
        security_profile.save()


user_logged_in.connect(user_logged_in_handler)

class Biometric(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='biometric')
    timestamp = models.DateTimeField(default=timezone.now)
    session_key = models.CharField(max_length=100, default='')
    valid = models.BooleanField(default=True)
    history = HistoricalRecords()

class Pincode(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pincodes')
    timestamp = models.DateTimeField(default=timezone.now)
    session_key = models.CharField(max_length=100, default='')
    valid = models.BooleanField(default=True)
    history = HistoricalRecords()

class MRZScan(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='mrz_scans')
    timestamp = models.DateTimeField(default=timezone.now)
    session_key = models.CharField(max_length=100, default='', blank=True, null=True)
    image = models.ImageField(default=None, null=True, blank=True, upload_to=get_document_path)
    barcode_data = models.TextField(blank=True, default='')
    ocr_data = models.TextField(blank=True, default='')
    ocr_key = models.TextField(blank=True, default='')
    valid = models.BooleanField(default=True)
    history = HistoricalRecords()

    def get_barcode_url(self):
        path, url = get_private_secure_path(self.image.name)
        full_path = os.path.join(settings.BASE_DIR, path)
        shutil.copy(self.image.path, full_path)
        from lotteh.celery import remove_secure
        remove_secure.apply_async([full_path], countdown=settings.REMOVE_SECURE_TIMEOUT_FILE_SECONDS)
        return url #reverse('feed:secure-photo', kwargs={'filename': url})

    def delete(self):
        if self.image:
            try:
                os.remove(self.image.path)
            except: pass
        super(MRZScan, self).delete();

class NFCScan(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='nfc_scans')
    timestamp = models.DateTimeField(default=timezone.now)
    session_key = models.CharField(max_length=100, default='', blank=True, null=True)
    nfc_id = models.TextField(blank=True, default='')
    nfc_data_read = models.TextField(blank=True, default='')
    nfc_data_written = models.TextField(blank=True, default='')
    nfc_id = models.TextField(blank=True, default='')
    nfc_name = models.TextField(blank=True, default='')
    valid = models.BooleanField(default=True)
    history = HistoricalRecords()

class UserIpAddress(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(default=timezone.now)
    last_updated_sun = models.DateTimeField(default=timezone.now)
    sunrise = models.DateTimeField(default=timezone.now)
    sunset = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.CharField(max_length=39,default='', null=True, blank=True)
    session_key = models.CharField(max_length=36, default='')
    timezone = models.CharField(max_length=32,default='', null=True, blank=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    risk_detected = models.BooleanField(default=False)
    risk_count = models.IntegerField(default=0)
    risk_recheck = models.BooleanField(default=False)
    fraudguard_data = models.TextField(blank=True, default='')
    page_loads = models.IntegerField(default=0)
    verified = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return 'user @{} ip {} detected risk? {} with {} page loads'.format(self.user.username if self.user else 'guest user', self.ip_address, self.risk_detected, self.page_loads)

class SecurityProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='security_profile')
    session_key = models.CharField(max_length=100, default='')
    ip_addresses = models.ManyToManyField(UserIpAddress, related_name='ip_addresses', blank=True)
    profile_call = models.DateTimeField(default=timezone.now)
    pin_entered = models.DateTimeField(default=timezone.now)
    pin_entered_incorrectly = models.DateTimeField(default=timezone.now)
    incorrect_pin_attempts = models.IntegerField(default=0)
    pincode = models.TextField(default='')
    biometrics_enabled = models.BooleanField(default=False)
    history = HistoricalRecords()

class Session(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions')
    ip_address = models.CharField(max_length=39, default='')
    index = models.IntegerField(default=0)
    uuid_key = models.CharField(max_length=36, default='', null=True)
    http_referrer = models.TextField(default='', null=True)
    content_length = models.TextField(default='', null=True, blank=True)
    path = models.TextField(default='')
    querystring = models.TextField(default='')
    time = models.DateTimeField(default=timezone.now)
    method = models.CharField(max_length=10, default='GET')
    injection = models.TextField(null=True, default='')
    past_injections = models.TextField(null=True, default='')
    injection_key = models.CharField(max_length=36, default='')
    injected = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        username = 'guest user'
        if self.user:
            username = self.user.username
        return 'id {} uuid {} user @{} ip {} time {}'.format(self.id, self.uuid_key, username, self.ip_address, self.time.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime("%m/%d/%Y, %H:%M:%S"))

class SessionDedup(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='dedup_sessions')
    ip_address = models.CharField(max_length=39, default='')
    path = models.TextField(default='')
    querystring = models.TextField(default='')
    method = models.CharField(max_length=10, default='GET')
    time = models.DateTimeField(default=timezone.now)

    def async_delete(self):
        from lotteh.celery import delay_delete_session
        delay_delete_session.apply_async([self.id], countdown=30)

admin.site.register(Session)

