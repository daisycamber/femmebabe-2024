import requests, json, base64, os
from django.conf import settings

def get_as_base64(url):
    return base64.b64encode(requests.get(url).content)

def upload_photo_old(path):
    files = {'image': ('{}.png'.format(settings.DOMAIN), open(path, 'rb'), 'image/png')}
    out = requests.post('https://api.imgbb.com/1/upload?key={}'.format(settings.IMAGE_HOST_KEY), files=files)
    j = out.json()
    print(json.dumps(j))
    if j and 'data' in j:
        return j['data']['image']['url'], j['data']['thumb']['url']
    return None, None

MAX_UPLOAD = 1500

def upload_photo(path):
    import cloudinary, base64, json, uuid, cv2
    import cloudinary.uploader
    from cloudinary.utils import cloudinary_url
    from django.conf import settings
    cloudinary.config(
        cloud_name = settings.CLOUDINARY_CLOUD_NAME,
        api_key = settings.CLOUDINARY_API_KEY,
        api_secret = settings.CLOUDINARY_API_SECRET,
        secure=True
        )
    image = cv2.imread(path)
    height, width = image.shape[:2]
    new_width = width
    new_height = height
    greatest = width if width > height else height
    if greatest > MAX_UPLOAD:
        new_width = int(width * (MAX_UPLOAD/greatest))
        new_height = int(height * (MAX_UPLOAD/greatest))
    resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    retval, buffer = cv2.imencode('.png', resized_image)
    data = 'data:image/png;base64,' + base64.b64encode(buffer).decode('utf-8')
#    print(data[:100])
    uid = str(uuid.uuid4())
    upload_result = cloudinary.uploader.upload(data, public_id=uid)
    auto_crop_url, _ = cloudinary_url(uid, width=500, height=500, crop="auto", gravity="auto")
#    print(json.dumps(upload_result))
#    print(upload_result["secure_url"])
    return str(upload_result['secure_url']), str(auto_crop_url)

def upload_post(post):
    import traceback
    if post.image_bucket or (post.image and os.path.exists(post.image.path)):
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
#        except: print(traceback.format_exc())
        print('Uploaded post ({}). - {}'.format(post.id, post.image_offsite))
        return True
    return False

def upload_posts():
    from feed.models import Post
    for post in Post.objects.filter(published=True).order_by('-date_posted'):
        if not (post.image_offsite and len(post.image_offsite) > 0): # or (post.image and os.path.exists(post.image.path):
            try: upload_post(post)
            except: pass
