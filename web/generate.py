import os
from feed.models import Post
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User

def generate_site():
    images = ''
    count = 0
    for post in Post.objects.filter(uploaded=True, public=True, offsite=True, posted=True, published=True, feed="private").exclude(image_bucket=None).order_by('-date_posted'):
        images = images + '<div id="div{}"><p>{}</p><img width="100%" height="auto" src="{}" id="img{}"></div>\n'.format(count, post.content.replace('\n', ' '), post.image_offsite, count)
        count = count + 1
    context = {
        'site_name': settings.STATIC_SITE_NAME,
        'static_url': settings.STATIC_SITE_URL,
        'base_url': settings.BASE_URL,
        'author_name': settings.AUTHOR_NAME,
        'images': images,
        'model_name': User.objects.get(id=settings.MY_ID).profile.name,
        'model': User.objects.get(id=settings.MY_ID),
    }
    index = render_to_string('web/index.html', context)
    with open(os.path.join(settings.BASE_DIR, 'web/site/', 'index.html'), 'w') as file:
        file.write(index)
