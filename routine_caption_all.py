import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lotteh.settings')

import django
django.setup()
from enhance.caption import routine_caption_image
from feed.models import Post
for post in Post.objects.filter(content='').exclude(image=None):
    routine_caption_image()
