import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lotteh.settings')
import django
django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

u = User.objects.get(id=settings.MY_ID)
p = u.profile
p.identity_verification_expires = timezone.now() + datetime.timedelta(hours=24*30*3)
p.identity_verified = True
p.id_front_scanned = True
p.id_back_scanned = True
p.save()
