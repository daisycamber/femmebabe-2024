import requests, json, base64
from django.conf import settings
from feed.models import Post

def get_as_base64(url):
    return base64.b64encode(requests.get(url).content)

def upload_post(post):
    if post.image and post.image_bucket:
        post.download_photo()
        files = {'image': ('{}.png'.format(settings.DOMAIN), open(post.image.path, 'rb'), 'image/png')}
        out = requests.post('https://api.imgbb.com/1/upload?key={}'.format(settings.IMAGE_HOST_KEY), files=files)
#        print(out)
        j = out.json()
        if j and 'data' in j:
            post.image_offsite = j['data']['image']['url']
            post.image_thumb_offsite = j['data']['thumb']['url']
            post.offsite = True
            post.save()
            return True
    return False

def upload_posts():
    for post in Post.objects.filter(uploaded=True, public=True, offsite=False, posted=True, published=True).exclude(image_bucket=None):
        upload_post(post)

