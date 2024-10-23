import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lotteh.settings')
import django
django.setup()

from users.patch import patch_users
patch_users('lotteh2024')
