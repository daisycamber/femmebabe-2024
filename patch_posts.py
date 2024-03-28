ID = 2
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'femmebabe.settings')
import django
django.setup()
from feed.models import Post

for post in Post.objects.all():
    if post.image_thumbnail:
        post.image_thumbnail = str(post.image_thumbnail.path).replace('uglek', 'femmebabe')
        post.save()