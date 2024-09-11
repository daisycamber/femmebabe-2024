ID = 2
import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lotteh.settings')
import django
django.setup()

import datetime
from django.utils import timezone
from shell.models import ShellLogin
s = ShellLogin.objects.filter(time__gte=timezone.now() - datetime.timedelta(minutes=5), validated=False).order_by('time')[int(sys.argv[1])-1]
if s:
    s.validated = True
    s.approved = True
    s.save()
    print('Login approved')
else:
    print('No login found')
