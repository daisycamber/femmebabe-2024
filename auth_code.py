ID = 2
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lotteh.settings')
import django
django.setup()
from django.contrib.auth.models import User
print(User.objects.get(id=ID).mfa_tokens.last().token)
