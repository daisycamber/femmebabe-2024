from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class Camera(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='photobooth_camera')
    name = models.CharField(default="", null=True, blank=True, max_length=100)
    data = models.TextField(default="", null=True, blank=True)
    connected = models.DateTimeField(default=timezone.now)
