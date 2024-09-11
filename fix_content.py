import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clemn.settings')

import django
django.setup()
from feed.models import Post
import re
replace = {'man': 'woman', 'boy': 'woman', 'his': 'her'}
for post in Post.objects.all():
    if post.content != "":
        content = post.content
        for key, value in replace.items():
            content = re.sub('\s' + key + '\s', ' ' + value + ' ', content)
        if content != post.content:
            post.content = content
            post.save()