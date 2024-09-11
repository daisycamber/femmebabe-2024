ID = 2
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lotteh.settings')
import django
django.setup()

import datetime
from django.utils import timezone
from shell.models import ShellLogin
for s in ShellLogin.objects.filter(time__gte=timezone.now() - datetime.timedelta(minutes=5), validated=False):
    s.validated = True
    s.approved = False
    s.save()
