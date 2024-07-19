from django.contrib import admin
from django.db import models
from django.utils import timezone
import datetime
import pytz
from django.conf import settings
import uuid
import os
from django.contrib.auth.models import User

class ScheduledEmail(models.Model):
    id = models.AutoField(primary_key=True)
    recipient = models.CharField(blank=True, max_length=255)
    subject = models.CharField(blank=True, max_length=255)
    content = models.TextField(blank=True)
    send_at = models.DateTimeField(default=timezone.now)
    sent = models.BooleanField(default=False)

    def send(self):
        from users.email import send_html_email_template, send_vendor_email
        if self.sent: return
        if self.recipient:
            send_vendor_email(self.recipient, self.subject, self.content)
        else:
            users = User.objects.filter(is_active=True, profile__email_verified=True, profile__subscribed=True)
            for user in users:
                send_html_email_template(user, self.subject, self.content)
        self.sent = True
        self.save()

admin.site.register(ScheduledEmail)

class ScheduledUserEmail(models.Model):
    id = models.AutoField(primary_key=True)
    recipient = models.ForeignKey(User, null=True, blank=True, related_name='scheduled_emails_inbox', on_delete=models.CASCADE)
    subject = models.CharField(blank=True, max_length=255)
    content = models.TextField(blank=True)
    send_at = models.DateTimeField(default=timezone.now)
    sent = models.BooleanField(default=False)

    def send(self):
        from users.email import send_html_email_template, send_email
        if self.sent: return
        if self.recipient:
            send_html_email_template(self.recipient, self.subject, self.content)
        self.sent = True
        self.save()

admin.site.register(ScheduledUserEmail)
