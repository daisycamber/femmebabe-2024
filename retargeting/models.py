from simple_history.models import HistoricalRecords
from django.contrib import admin
from django.db import models
from django.utils import timezone
import datetime
import pytz
from django.conf import settings
import uuid
import os
from django.contrib.auth.models import User
from users.username_generator import generate_username as get_random_username


class ScheduledEmail(models.Model):
    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='scheduled_emails', null=True, blank=True)
    recipient = models.CharField(blank=True, max_length=255)
    subject = models.CharField(blank=True, max_length=255)
    content = models.TextField(blank=True)
    send_at = models.DateTimeField(default=timezone.now)
    sent = models.BooleanField(default=False)
    history = HistoricalRecords()

    def send(self):
        from users.email import send_html_email_template, send_html_email_backend, send_html_email_backend_template
        if self.sent: return
        if len(self.recipient.replace(' ','').split(',')) > 1:
            for recipient in self.recipient.replace(' ','').split(','):
                if not User.objects.filter(email=recipient).count():
                    from users.models import Profile
                    from security.models import SecurityProfile
                    user = User.objects.create_user(email=recipient, username=get_random_username(), password=get_random_string(8))
                    if not has_attr(user, 'profile'):
                        p = Profile.objects.get_or_create(user=user)
                        p.email_verified = False
                        p.finished_signup = False
                        p.subscribed = True
                        p.save()
                    if not has_attr(user, 'security_profile'):
                        SecurityProfile.objects.get_or_create(user=user)
                user = User.objects.filter(email=recipient).order_by('-date_posted')
                if user.subscribed:
                    send_html_email_backend(self.sender, recipient, self.subject, self.content)
        elif self.recipient:
            send_html_email_backend(self.sender, self.recipient, self.subject, self.content)
        else:
            users = User.objects.filter(is_active=True, profile__email_verified=True, profile__subscribed=True)
            for user in users:
                send_html_email_template(user, self.subject, self.content)
        self.sent = True
        self.save()


class ScheduledUserEmail(models.Model):
    id = models.AutoField(primary_key=True)
    recipient = models.ForeignKey(User, null=True, blank=True, related_name='scheduled_emails_inbox', on_delete=models.CASCADE)
    subject = models.CharField(blank=True, max_length=255)
    content = models.TextField(blank=True)
    send_at = models.DateTimeField(default=timezone.now)
    sent = models.BooleanField(default=False)
    history = HistoricalRecords()

    def send(self):
        from users.email import send_html_email_template, send_email
        if self.sent: return
        if self.recipient:
            send_html_email_template(self.recipient, self.subject, self.content)
        self.sent = True
        self.save()

