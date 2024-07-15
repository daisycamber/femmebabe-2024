import os
from django.utils.crypto import get_random_string
from django.conf import settings
from feed.middleware import get_current_user
from feed.middleware import get_current_request

def get_secure_public_path(filename):
    u = get_current_request().user.id if hasattr(get_current_request(), 'user') and get_current_request().user.is_authenticated else '0'
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (get_random_string(length=32) + '-{}'.format(u), ext)
    return os.path.join('media/secure/profile/', filename), '/media/secure/profile/{}'.format(filename)

def get_secure_video_path(filename):
    u = get_current_request().user.id if hasattr(get_current_request(), 'user') and get_current_request().user.is_authenticated else '0'
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (get_random_string(length=settings.SECURE_MEDIA_CODE_LENGTH) + '-{}'.format(u), ext)
    return os.path.join('media/secure/video/', filename), '/feed/secure/video/{}'.format(filename)

def get_secure_live_path(filename):
    u = get_current_request().user.id if hasattr(get_current_request(), 'user') and get_current_request().user.is_authenticated else '0'
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (get_random_string(length=settings.SECURE_MEDIA_CODE_LENGTH) + '-{}'.format(u), ext)
    return os.path.join('media/secure/video/', filename), '{}'.format(filename)

def get_secure_still_path(filename):
    u = get_current_request().user.id if hasattr(get_current_request(), 'user') and get_current_request().user.is_authenticated else '0'
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (get_random_string(length=settings.SECURE_MEDIA_CODE_LENGTH) + '-{}'.format(u), ext)
    return os.path.join('media/secure/video/', filename), '{}'.format(filename)

def get_secure_path(filename):
    u = get_current_request().user.id if hasattr(get_current_request(), 'user') and get_current_request().user.is_authenticated else '0'
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (get_random_string(length=settings.SECURE_MEDIA_CODE_LENGTH) + '-{}'.format(u), ext)
    return os.path.join('media/secure/media/', filename), '/feed/secure/photo/{}'.format(filename)

def get_private_secure_path(filename):
    u = get_current_request().user.id if hasattr(get_current_request(), 'user') and get_current_request().user.is_authenticated else '0'
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (get_random_string(length=settings.SECURE_MEDIA_CODE_LENGTH) + '-{}-s'.format(u), ext)
    return os.path.join('media/secure/media/', filename), '/feed/secure/photo/{}'.format(filename)

def get_secure_face_path(filename):
    u = get_current_request().user.id if hasattr(get_current_request(), 'user') and get_current_request().user.is_authenticated else '0'
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (get_random_string(length=settings.SECURE_MEDIA_CODE_LENGTH) + '-{}'.format(u), ext)
    return os.path.join('media/secure/face/', filename), '/face/secure/photo/{}'.format(filename)

def secure_remove_dir(path):
    dir = os.path.join(settings.BASE_DIR, path)
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))
