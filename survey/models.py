from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Survey(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.TextField(default='', null=True, blank=True)
    answers_seperated = models.TextField(default='', null=True, blank=True)
    priority = models.IntegerField(default=0)

class Answer(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='surveys', null=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='answers', null=True)
    answer = models.TextField(default='', null=True, blank=True)
    completed = models.BooleanField(default=False)
