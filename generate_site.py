uid = 2
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'femmebabe.settings')

import django
django.setup()
from web.generate import generate_site
generate_site()
