uid = 1
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lotteh.settings')

import django
django.setup()
from django.contrib.auth.models import User
from users.models import Profile
from django.conf import settings
u = User.objects.get(id=uid)
p = Profile.objects.get_or_create(user=u)
print(settings.BASE_URL + u.profile.create_auth_url())
