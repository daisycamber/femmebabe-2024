import requests, json, base64, os
from django.conf import settings

def get_as_base64(url):
    return base64.b64encode(requests.get(url).content)

def upload_photo(path):
    files = {'image': ('{}.png'.format(settings.DOMAIN), open(path, 'rb'), 'image/png')}
    out = requests.post('https://api.imgbb.com/1/upload?key={}'.format(settings.IMAGE_HOST_KEY), files=files)
    j = out.json()
    print(json.dumps(j))
    if j and 'data' in j:
        return j['data']['image']['url'], j['data']['thumb']['url']
    return None, None

def upload_post(post):
    if post.image and post.image_bucket:
        post.download_photo()
        if not post.image_censored or not os.path.exists(post.image_censored.path):
            post.image_censored = None
            post.image_censored_bucket = None
            post.image_offsite = None
            post.save()
            post.get_blur_url()
        i1, i2 = upload_photo(post.image.path if post.public else post.image_censored.path)
        post.image_offsite = i1
        post.image_thumb_offsite = i2
        post.offsite = True
        post.save()
        return True
    return False

def upload_posts():
    from feed.models import Post
    for post in Post.objects.filter(uploaded=True, public=True, offsite=False, posted=True, published=True).exclude(image_bucket=None):
        upload_post(post)

