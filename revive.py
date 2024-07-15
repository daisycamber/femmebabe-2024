import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'femmebabe.settings')
import django
django.setup()
from django.contrib.auth.models import User
from django.conf import settings
from femmebabe.celery import start_server
start_server()
