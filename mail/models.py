from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class LastUpdatedMail(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE, related_name='updated_mail')
    count = models.IntegerField(default=-1)
    updated = models.DateTimeField(default=timezone.now)
