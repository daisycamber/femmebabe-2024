import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clemn.settings')
import django
django.setup()
from django.conf import settings
from femmebabe.celery import process_recordings
process_recordings()