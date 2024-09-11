import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lotteh.settings')

import django
django.setup()
from django.contrib.auth.models import User
from django.conf import settings
un = ''
for user in User.objects.all():
    un += user.username + ',' + user.email + '\n'
with open('email_list.txt', 'w') as file:
    file.write(un)
file.close()
