from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid
import os, shutil
from security.secure import get_secure_public_path
from django.conf import settings

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('voice/', filename)

class Call(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='calls')
    sid = models.TextField(default='', null=True, blank=True)
    call_time = models.DateTimeField(default=timezone.now, null=True, blank=True)

class VoiceProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='voice_profile')
    last_call = models.DateTimeField(default=None, null=True, blank=True)
    recordings = models.BooleanField(default=False)
    interactive = models.TextField(default='', null=True, blank=True)
    call_logs = models.TextField(default='', null=True, blank=True)

class Choice(models.Model):
    option = models.TextField(default='', null=True, blank=True)
    number = models.IntegerField(default=1, null=True, blank=True)
    def __str__(self):
        return self.option + ' - \#' + self.number

class UserChoice(Choice):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='voice_choices')
    def __str__(self):
        return 'user @{} option {} \#{}'.format(self.user.username, self.option, self.number)

class AudioInteractive(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    label = models.TextField(default='', null=True, blank=True)
    interactive = models.TextField(default='', null=True, blank=True)
    choices = models.ManyToManyField(UserChoice, blank=True)
    content = models.FileField(upload_to=get_file_path, null=True, blank=True)
    uploaded_file = models.DateTimeField(default=timezone.now)

    def get_secure_url(self):
        path, url = get_secure_public_path(self.content.name)
        full_path = os.path.join(settings.BASE_DIR, path)
        if '..' in str(self.content.path):
            self.content = str(self.content.path).replace('..','.')
            self.save()
        shutil.copy(self.content.path, full_path)
        from lotteh.celery import remove_secure
        remove_secure.apply_async([full_path], countdown=30)
        return url

    def __str__(self):
        content = ''
        for choice in self.choices.all():
            content = content +'\#{} - {}'.format(choice.number, choice.option) + ' / '
        return 'user @ {} label {} & interactive * {}, {}'.format(self.user.username, self.label, self.interactive, content)
