from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Click(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clicks')
    path = models.TextField(null=True, blank=True)
    element = models.CharField(max_length=50)
    timestamp = models.DateTimeField(default=timezone.now)
