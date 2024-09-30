import requests, json, base64, os
from django.conf import settings

def resize_image(image_path):
    from PIL import Image
    img = Image.open(image_path)
    output_size = (settings.MAX_RED_IMAGE_DIMENSION, settings.MAX_RED_IMAGE_DIMENSION)
    max = img.width
    if img.height < img.width:
        max = img.height
    from feed.crop import crop_center
    img = crop_center(img,max,max)
    img.save(image_path)
    img = Image.open(image_path)
    img.thumbnail(output_size)
    return img

def get_as_base64(url):
    return base64.b64encode(requests.get(url).content)

def upload_photo(path):
    with open(path, "rb") as file:
        data = file.read()
        image1 = base64.b64encode(data)
    from io import BytesIO
    buffered = BytesIO()
    im = resize_image(path)
    im.save(buffered, format="PNG")
    image2 = base64.b64encode(buffered.getvalue())
    return upload(image1), upload(image2)

def upload(base64_data):
#    b64data = 'data:image/png;base64,' + base64_data.decode('utf-8')
    data = {
        'image': base64_data,
        'type': 'base64',
        'title': '{} - {}'.format(settings.SITE_NAME, settings.AUTHOR_NAME),
        'description': settings.BASE_DESCRIPTION + ' - from {}'.format(settings.STATIC_DOMAIN),
    }
    headers = {"Authorization": "Client-ID {}".format(settings.IMGUR_ID)}
    out = requests.post('https://api.imgur.com/3/image', data=data, headers=headers)
    print(out)
    j = out.json()
    if j['status'] == 200:
        return j['data']['link']
    return None

def upload_photo_old(path):
    files = {'image': ('{}.png'.format(settings.DOMAIN), open(path, 'rb'), 'image/png')}
    out = requests.post('https://api.imgbb.com/1/upload?key={}'.format(settings.IMAGE_HOST_KEY), files=files)
    print(out)
    j = out.json()
    if j and 'data' in j:
        return j['data']['image']['url'], j['data']['thumb']['url']
    return None, None

MAX_UPLOAD = 1500

def upload_photo_cloudinary(path):
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
            except:
                import traceback
                print(traceback.format_exc())

def upload_post_async():
    from feed.models import Post
    for post in Post.objects.filter(published=True).exclude(image_offsite=None).order_by('-date_posted'):
        if not (post.image_offsite and len(post.image_offsite) > 0): # or (post.image and os.path.exists(post.image.path):
            try:
                upload_post(post)
                return
            except:
                import traceback
                print(traceback.format_exc())
