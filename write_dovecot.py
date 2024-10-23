import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lotteh.settings')

import django
django.setup()
from mail.views import write_dovecot
write_dovecot()
