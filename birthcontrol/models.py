from django.contrib import admin
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models.functions import Length
import datetime
import pytz
from django.conf import settings
import uuid
import os
from django.core.validators import MinValueValidator, MaxValueValidator
models.TextField.register_lookup(Length, 'length')

def get_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('birthcontrol/', filename)

class BirthControlPill(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    notes = models.TextField(blank=True)
    notes_save = models.TextField(blank=True)
    time_taken = models.DateTimeField(default=timezone.now)
    reminders = models.IntegerField(default=0)
    taken_with_food = models.BooleanField(default=True)
    flow = models.BooleanField(default=False)
    intercourse = models.BooleanField(default=False)
    incontinence = models.BooleanField(default=False)
    temperature = models.FloatField(default=98.0)


    def short_time(self):
        return self.time_taken.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%H:%M:%S')

    def __str__(self):
        return 'Patient - {} took a birth control pill on {}'.format(self.patient.vendor_profile.full_name, self.time_taken.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime("%m/%d/%Y at %H:%M:%S"))

admin.site.register(BirthControlPill)


class BirthControlProfile(models.Model):
    patient = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='birthcontrol_profile')
    birth_control = models.ImageField(null=True, blank=True, upload_to=get_image_path)
    birth_control_current = models.ImageField(null=True, blank=True, upload_to=get_image_path)
    birth_control_uploaded = models.DateTimeField(default=timezone.now)
    birth_control_barcodes = models.TextField(blank=True)
    period_start = models.PositiveIntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(31)])
    reminders = models.IntegerField(default=0)
    reminder_time = models.DateTimeField(default=timezone.now)
    send_pill_reminder = models.BooleanField(default=True)
    send_sleep_reminder = models.BooleanField(default=True)
    temperature = models.FloatField(default=98.0)

    def __str__(self):
        return 'Patient - {} took birth control on {}'.format(self.patient.vendor_profile.full_name, self.birth_control_taken().astimezone(pytz.timezone(settings.TIME_ZONE)).strftime("%m/%d/%Y at %H:%M:%S"))

    def took_birth_control_today(self):
        if not self.last_pill_taken(): return False
        return self.last_pill_taken() + datetime.timedelta(minutes=1435) > timezone.now()

    def taking_birth_control(self):
        if BirthControlPill.objects.filter(patient=self.patient).count() > 0:
            return True
        return False

    def birth_control_taken(self):
        p = BirthControlPill.objects.filter(patient=self.patient).last()
        return p.time_taken if p else self.reminder_time

    def last_pill_taken(self):
        p = BirthControlPill.objects.filter(patient=self.patient)
        if p.count() > 0:
            return p.last().time_taken
        else:
            return False

    def delete(self):
        print('Cannot delete birth control profile')

    def save(self, *args, **kwargs):
        super(BirthControlProfile, self).save(*args, **kwargs)
