from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Error(models.Model):
    id = models.AutoField(primary_key=True)
    notes = models.TextField(default='', blank=True, null=True)
    stack_trace = models.TextField(default='', blank=True, null=True)
    user = models.ForeignKey(User, related_name='errors', on_delete=models.DO_NOTHING, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return 'Error at {} UTC tracing {}'.format(self.timestamp, self.stack_trace)
