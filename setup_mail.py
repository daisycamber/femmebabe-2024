ID = 2
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'femmebabe.settings')
import django
django.setup()

from mail.views import write_dovecot
write_dovecot()
