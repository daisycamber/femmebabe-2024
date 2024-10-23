from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Vibrator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='vibrator')
    setting = models.CharField(max_length=7,null=True, blank=True, default='128,128')
    last_set = models.DateTimeField(default=timezone.now)
