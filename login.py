import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lotteh.settings')

import django
django.setup()
from django.contrib.auth.models import User
from django.conf import settings
u = User.objects.get(id=settings.MY_ID)
u.is_active = True
u.save()
print('Login here:')
print(settings.BASE_URL + u.profile.create_auth_url())
