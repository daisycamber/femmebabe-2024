from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Contact(models.Model):
    id = models.AutoField(primary_key=True)
    date_sent = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=100, default='')
    email = models.CharField(max_length=100, default='')
    phone = models.CharField(max_length=20, default='')
    ip = models.CharField(max_length=15, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='contacts')
    message = models.TextField(default='')
