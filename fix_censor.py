import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lotteh.settings')

import django
django.setup()
from django.contrib.auth.models import User
from django.conf import settings
u = User.objects.get(id=settings.MY_ID)
from feed.models import Post

for p in Post.objects.filter(public=False, author=u):
    if p.image and not os.path.exists(p.image.path) and p.image_bucket: p.download_photo()
    elif not p.image: continue
    p.image_censored_bucket = None
    p.save()
    p.get_blur_url()
    if p.image_censored and os.path.exists(p.image_censored.path):
        towrite = p.image_censored_bucket.storage.open(p.image_censored.path, mode='wb')
        with p.image_censored.open('rb') as file:
            towrite.write(file.read())
        towrite.close()
        p.image_censored_bucket = p.image_censored.path
    try:
        p.get_blur_thumb_url()
        if p.image_censored_thumbnail and os.path.exists(p.image_censored_thumbnail.path):
            towrite = p.image_censored_thumbnail_bucket.storage.open(p.image_censored_thumbnail.path, mode='wb')
            with p.image_censored_thumbnail.open('rb') as file:
                towrite.write(file.read())
            towrite.close()
            p.image_censored_thumbnail_bucket = p.image_censored_thumbnail.path
    except: pass
    p.save()
#    print(p.image_censored_bucket.url)
