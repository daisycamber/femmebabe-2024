ID = 2
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lotteh.settings')
import django
django.setup()
from feed.models import Post
from voice.models import AudioInteractive

#for post in Post.objects.all():
#    if post.image_thumbnail:
#        post.image_thumbnail = str(post.image_thumbnail.path).replace('uglek', 'lotteh')
#        post.save()

for post in AudioInteractive.objects.all():
    if post.content:
        post.content = str(post.content.path).replace('uglek', 'lotteh')
        post.save()
