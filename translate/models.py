from django.db import models
from django.conf import settings

class CachedTranslation(models.Model):
    id = models.AutoField(primary_key=True)
    src = models.CharField(default=settings.DEFAULT_LANG, max_length=10)
    dest = models.CharField(default=settings.DEFAULT_LANG, max_length=10)
    src_content = models.TextField(default='')
    dest_content = models.TextField(default='')
    pronunciation = models.TextField(default='', blank=True, null=True)
