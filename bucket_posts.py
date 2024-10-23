import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lotteh.settings')

import django
django.setup()
from enhance.image import bucket_posts
from django.utils import timezone
import datetime
before = timezone.now()
bucket_posts()
after = timezone.now()
print(str(after - before))
