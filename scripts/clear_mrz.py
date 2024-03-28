import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'femmebabe.settings')

import django
django.setup()
from django.conf import settings

from security.models import MRZScan, NFCScan
MRZScan.objects.all().delete()
NFCScan.objects.all().delete()