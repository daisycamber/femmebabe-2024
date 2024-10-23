from simple_history.models import HistoricalRecords
from django.db import models
from django.contrib.auth.models import User
from live.models import Camera
from django.utils import timezone
import uuid, os
from birthcontrol.models import BirthControlPill
from django.core.validators import MinValueValidator, MaxValueValidator
from address.models import AddressField
from django.conf import settings

def get_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('verification/', filename)

class VendorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='vendor_profile')
    subscriptions = models.ManyToManyField(User, related_name='vendor_subscriptions', blank=True)
    is_onboarded = models.BooleanField(default=False)
    pronouns = models.CharField(max_length=50,default='They')
    pornhub_link = models.CharField(max_length=500,default='')
    onlyfans_link = models.CharField(max_length=500,default='')
    subscription_fee = models.CharField(max_length=50,default='50', null=True, blank=True)
    photo_tip = models.CharField(max_length=10, default='5', null=True, blank=True)
    free_trial = models.CharField(max_length=10, default=settings.DEFAULT_MODEL_TRIAL_DAYS, null=True, blank=True)
    compress_video = models.BooleanField(default=False)
    activate_surrogacy = models.BooleanField(default=False)
    hide_profile = models.BooleanField(default=False)
    payout_currency = models.CharField(max_length=10, default='BTC', null=True, blank=True)
    payout_address = models.CharField(max_length=300, default='', null=True, blank=True)
    pitch_adjust = models.IntegerField(default=0)
    address = AddressField(null=True, blank=True)
    insurance_provider = models.CharField(max_length=300, default='', null=True, blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.user.profile.name

    def taking_birth_control(self):
        if BirthControlPill.objects.filter(patient=self.user).count() > 0:
            return True
        return False

    def birth_control_taken(self):
        return BirthControlPill.objects.filter(patient=self.user).last().time_taken

    def delete(self):
        print('Cannot delete vendor profile')

    def save(self, *args, **kwargs):
        super(VendorProfile, self).save(*args, **kwargs)
