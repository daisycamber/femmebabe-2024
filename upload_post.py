import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lotteh.settings')

import django
django.setup()
from feed.upload import upload_post_async
from django.utils import timezone
import datetime
before = timezone.now()
upload_post_async()
after = timezone.now()
print(str(after - before))
