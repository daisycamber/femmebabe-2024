import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'femmebabe.settings')

import django
django.setup()
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.sessions.models import Session
Session.objects.all().delete()
