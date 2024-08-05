uid = 2
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lotteh.settings')

import django
django.setup()
from django.contrib.auth.models import User
from django.conf import settings
u = User.objects.get(id=uid)
u.is_active = True
u.profile.identity_verified = True
u.profile.id_front_scanned = True
u.profile.id_back_scanned = True
u.profile.save()
u.save()
print('ID Validated')
