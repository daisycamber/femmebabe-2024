import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lotteh.settings')

import django
django.setup()
from enhance.caption import routine_caption_image
routine_caption_image()
