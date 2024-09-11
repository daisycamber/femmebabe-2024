uid = 2
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lotteh.settings')

import django
django.setup()
from feed.models import Post
print(Post.objects.all().count())
