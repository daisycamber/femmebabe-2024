ID = 2
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'femmebabe.settings')
import django
django.setup()

import datetime, pytz
from django.conf import settings
from django.utils import timezone
from shell.models import ShellLogin
s = ShellLogin.objects.filter(time__gte=timezone.now() - datetime.timedelta(minutes=3))
op = ''
for login in s.order_by('-time'):
    op = op + 'At {} from {}'.format(login.time.astimezone(pytz.timezone(settings.TIME_ZONE)),login.ip_address) + '\n'

print(op if op else 'None')
