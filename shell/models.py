from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class SavedFile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='file_edits', null=True)
    path = models.CharField(default='', null=True, blank=True, max_length=255)
    content = models.TextField(null=True, blank=True, default='')
    saved_at = models.DateTimeField(default=timezone.now)
    current = models.BooleanField(default=True)

class ShellLogin(models.Model):
    id = models.AutoField(primary_key=True)
    ip_address = models.CharField(max_length=39, default='', null=True, blank=True)
    time = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)
    validated = models.BooleanField(default=False)
