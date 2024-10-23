from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from feed.models import Post

class Game(models.Model):
    id = models.AutoField(primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='games')
    time = models.DateTimeField(default=timezone.now)
    uid = models.CharField(max_length=10, default='')
    code = models.CharField(max_length=10, default='')
    begun = models.BooleanField(default=False)
    players = models.IntegerField(default=0, null=True)
    turn = models.TextField(default='')
    turns = models.TextField(default='')
