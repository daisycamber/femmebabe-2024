import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lotteh.settings')

import django
django.setup()
from enhance.image import routine_enhance_post
from django.utils import timezone
import datetime
from feed.models import Post
while Post.objects.filter(enhanced=False, published=True).count() > 0:
    before = timezone.now()
    routine_enhance_post()
    after = timezone.now()
    print(str(after - before))
