import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lotteh.settings')
import django
django.setup()
from django.contrib.auth.models import User
from django.conf import settings
from feed.models import Post
user = User.objects.get(id=settings.MY_ID)
for post in Post.objects.filter(author=user, published=False):
    post.published = True
    post.save()
