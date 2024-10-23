from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid

class Choice(models.Model):
    option = models.TextField(default='', null=True, blank=True)
    def __str__(self):
        return self.option

class UserChoice(Choice):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return 'user @{} option {}'.format(self.user.username, self.option)

class Choices(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    label = models.TextField(default='', null=True, blank=True)
    interactive = models.TextField(default='', null=True, blank=True)
    choices = models.ManyToManyField(UserChoice, symmetrical=False, blank=True)
    def __str__(self):
        content = ''
        for choice in self.choices.all():
            content = content + choice.option + ' / '
        return 'user @ {} label {} & interactive * {}, {}'.format(self.user.username, self.label, self.interactive, content)
