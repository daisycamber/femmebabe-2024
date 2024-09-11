import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lotteh.settings')

import django
django.setup()
from feed.upload import upload_posts
from django.utils import timezone
import datetime
before = timezone.now()
upload_posts()
after = timezone.now()
print(str(after - before))
