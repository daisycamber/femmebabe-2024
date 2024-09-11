from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.contrib import admin
# Create your models here.

class Message(models.Model):
    lang = None
    id = models.AutoField(primary_key=True)
    sent_at = models.DateTimeField(default=timezone.now)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender', null=True, blank=True)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipient', null=True, blank=True)
    content = models.TextField(default="", null=True, blank=True)
    seen = models.BooleanField(default=False)
    senderseen = models.BooleanField(default=False)
    def __str__(self):
        return '{} says to {}, {}'.format(self.sender, self.recipient, self.content)

    def sent_at_format(self):
        return self.sent_at.strftime('%B %d, %Y, %H:%M:%S')

    def get_content(self):
        from translate.translate import translate
        return translate(None, self.content, self.lang, self.lang)

    def get_direct_link(self):
        from translate.translate import translate
        return reverse('chat:chat', kwargs={'username': self.sender.profile.name})

    def get_direct_text(self):
        from translate.translate import translate
        return translate(None, 'Direct', self.lang, self.lang)

    def get_delete_text(self):
        from translate.translate import translate
        return translate(None, 'Delete', self.lang, self.lang)

admin.site.register(Message)

from django.contrib.auth.hashers import make_password, check_password


class Key(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(default=timezone.now)
    keyed_at = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(default=timezone.now)
    name = models.CharField(default="", max_length=100, null=True, blank=True)
    key = models.CharField(default="", max_length=255, null=True, blank=True)
    age = models.IntegerField(default=0)
    sex = models.CharField(default="", max_length=10, null=True, blank=True)
    permitted = models.BooleanField(default=True)

    def set_password(self, raw_password):
        self.key = make_password(raw_password)
        self.save()

    def check_password(self, key):
        if not self.key: self.set_password(key)
        return check_password(key, self.key)

admin.site.register(Key)
