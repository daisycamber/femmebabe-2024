import traceback, os, shutil
from django.core.files.base import ContentFile
from django.core.files import File
from shell.execute import run_command
from django.conf import settings

def enhance_image(image_path):
#    from enhance.superres import superres, superres_x4
    from enhance.denoise import denoise
    from face.deep import is_face
#    from enhance.gfpgan import gfpgan_enhance
    print('denoise')
    try: denoise(image_path)
    except: print('Failed to denoise')
#    print('gfpgan')
#    run_command('sudo disgpu')
#    try: gfpgan_enhance(image_path)
#    except: print(traceback.format_exc())
#    print('superres')
#    run_command('sudo enagpu')
#    try: superres_x4(image_path)
#    except: print(traceback.format_exc())

def enhance_post(post_id):
    from feed.models import Post
    from feed.align import face_rotation
    from feed.upload import upload_post
    p = Post.objects.get(id=post_id)
    print('Post ID {}'.format(post_id))
    if p.enhanced and not p.uploaded:
        bucket_post(p.id)
        return
    if p.enhanced: return
    print('test')
    if p.uploaded and (not p.image or not os.path.exists(p.image.path)): p.download_original()
    elif not p.image and not os.path.exists(p.image.path): return
    run_command('sudo chown {}:users {}'.format(settings.BASH_USER, p.image.path))
    run_command('sudo chown {}:users {}'.format(settings.BASH_USER, p.image_original.path))
    if p.image_original and os.path.exists(p.image_original.path): shutil.copy(p.image_original.path, p.image.path)
    print('rotate')
    from face.deep import is_face
    if is_face(p.image.path):
        rot = face_rotation(p.image.path)
        if rot == 1:
            p.rotate_left()
        elif rot == -1:
            p.rotate_right()
        elif rot == 2:
            p.rotate_flip()
    print('enhance')
    enhance_image(p.image.path)
    p.enhanced = True
    p.save()
    try:
        os.remove(p.image_censored.path)
    except: pass
    try:
        os.remove(p.image_censored_thumbnail.path)
    except: pass
    try:
        os.remove(p.image_thumbnail.path)
    except: pass
    try:
        os.remove(p.image_public.path)
    except: pass
    p.image_censored = None
    p.image_censored_thumbnail = None
    p.image_thumbnail = None
    p.image_public = None
    if not p.image or not os.path.exists(p.image.path):
        p.uploaded = True
        p.enhanced = True
        if Post.objects.filter(id=post_id).first(): p.save()
        return
    towrite = p.image_bucket.storage.open(p.image.path, mode='wb')
    with p.image.open('rb') as file:
        towrite.write(file.read())
    towrite.close()
    p.image_bucket = p.image.path
    if p.image_original and os.path.exists(p.image_original.path):
        towrite = p.image_original_bucket.storage.open(p.image_original.path, mode='wb')
        with p.image_original.open('rb') as file:
            towrite.write(file.read())
        towrite.close()
        p.image_original_bucket = p.image_original.path
    p.get_image_thumb_url()
    if p.image_thumbnail and os.path.exists(p.image_thumbnail.path):
        towrite = p.image_thumbnail_bucket.storage.open(p.image_thumbnail.path, mode='wb')
        with p.image_thumbnail.open('rb') as file:
            towrite.write(file.read())
        towrite.close()
        p.image_thumbnail_bucket = p.image_thumbnail.path
    p.get_face_blur_thumb_url()
    if p.image_public and os.path.exists(p.image_public.path):
        towrite = p.image_public_bucket.storage.open(p.image_public.path, mode='wb')
        with p.image_public.open('rb') as file:
            towrite.write(file.read())
        towrite.close()
        p.image_public_bucket = p.image_public.path
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
    p.uploaded = True
    if Post.objects.filter(id=post_id).first(): p.save()
    upload_post(p)
#    bucket_post(p.id)
    try:
        os.remove(p.image_censored_thumbnail.path)
    except: pass
    try:
        os.remove(p.image_thumbnail.path)
    except: pass
    try:
        os.remove(p.image_original.path)
    except: pass
    try:
        os.remove(p.image_censored.path)
    except: pass
    try:
        os.remove(p.image_public.path)
    except: pass
    try:
        os.remove(p.image.path)
    except: pass
    print('Finished enhancing post.')

def bucket_post(post_id):
    from feed.models import Post
    from feed.upload import upload_post
    p = Post.objects.get(id=post_id)
    try:
        if not p.image or not os.path.exists(p.image.path):
            p.enhanced = True
            p.uploaded = True
            p.save()
            return
    except: return
    try:
        os.remove(p.image_censored.path)
    except: pass
    try:
        os.remove(p.image_censored_thumbnail.path)
    except: pass
    try:
        os.remove(p.image_thumbnail.path)
    except: pass
    try:
        os.remove(p.image_public.path)
    except: pass
    p.image_censored = None
    p.image_censored_thumbnail = None
    p.image_thumbnail = None
    p.image_public = None
    if not p.image or not os.path.exists(p.image.path):
        p.uploaded = True
        p.enhanced = True
        if Post.objects.filter(id=post_id).first(): p.save()
        return
    towrite = p.image_bucket.storage.open(p.image.path, mode='wb')
    with p.image.open('rb') as file:
        towrite.write(file.read())
    towrite.close()
    p.image_bucket = p.image.path
    if p.image_original and os.path.exists(p.image_original.path):
        towrite = p.image_original_bucket.storage.open(p.image_original.path, mode='wb')
        with p.image_original.open('rb') as file:
            towrite.write(file.read())
        towrite.close()
        p.image_original_bucket = p.image_original.path
    p.get_image_thumb_url()
    if p.image_thumbnail and os.path.exists(p.image_thumbnail.path):
        towrite = p.image_thumbnail_bucket.storage.open(p.image_thumbnail.path, mode='wb')
        with p.image_thumbnail.open('rb') as file:
            towrite.write(file.read())
        towrite.close()
        p.image_thumbnail_bucket = p.image_thumbnail.path
    p.get_face_blur_thumb_url()
    if p.image_public and os.path.exists(p.image_public.path):
        towrite = p.image_public_bucket.storage.open(p.image_public.path, mode='wb')
        with p.image_public.open('rb') as file:
            towrite.write(file.read())
        towrite.close()
        p.image_public_bucket = p.image_public.path
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
    p.uploaded = True
    if Post.objects.filter(id=post_id).first(): p.save()
    upload_post(p)
    if not p.enhanced: return
    try:
        os.remove(p.image_censored_thumbnail.path)
    except: pass
    try:
        os.remove(p.image_thumbnail.path)
    except: pass
    try:
        os.remove(p.image_original.path)
    except: pass
    try:
        os.remove(p.image_censored.path)
    except: pass
    try:
        os.remove(p.image_public.path)
    except: pass
    try:
        os.remove(p.image.path)
    except: pass

def bucket_posts():
    from feed.models import Post
    posts = Post.objects.filter(uploaded=False).order_by('-date_posted')
#    posts = Post.objects.filter(enhanced=True).order_by('-date_posted')
    for post in posts:
        try:
            if post.image and os.path.exists(post.image.path): # and post.enhanced:
                bucket_post(post.id)
        except: pass

def routine_enhance_post():
    from feed.models import Post
    posts = Post.objects.filter(enhanced=False).order_by('-date_posted')
    print('Enhancing post')
    for post in posts:
        if post.image and (os.path.exists(post.image.path) or post.image_bucket):
            enhance_post(post.id)
            post.enhanced = True
            post.save()
            return


def routine_enhance_all():
    from feed.models import Post
    posts = Post.objects.filter(enhanced=False).order_by('-date_posted')
    for post in posts: routine_enhance_post()
