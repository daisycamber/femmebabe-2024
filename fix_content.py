import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lotteh.settings')
import django
django.setup()
from feed.models import Post
import re
replace = {'man': 'woman', 'boy': 'woman', 'his': 'her', 'man\'s': 'woman\'s', 'men': 'women', 'him': 'her', 'beard': 'piercing', 'knife': 'pose', 'mustache': 'makeup', 'a makeup': 'makeup', 'with makeup': 'wearing makeup', 'dog': 'phone'}

for post in Post.objects.all():
    if post.content != "":
        caption_text = post.content
        for key, value in replace.items():
            caption_text = re.sub('\s' + key + '\s', ' ' + value + ' ', caption_text)
            caption_text = re.sub('\s' + key + '\.', ' ' + value + '.', caption_text)
            caption_text = re.sub('\s' + key + '\,', ' ' + value + ',', caption_text)
        if caption_text != post.content:
            post.content = caption_text
            post.save()
