import os
from django.utils.crypto import get_random_string
from django.conf import settings

def get_email_path(filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (get_random_string(length=16), ext)
    return os.path.join(settings.BASE_DIR, 'email/', filename), '/email/{}'.format(filename)
