import django
django.setup()
from django.contrib.auth.models import User
from users.tfa import send_user_text
from django.utils import timezone

weekdays = ['none', 'Monday', 'Tuesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

def send_text():
    send_user_text(User.objects.get(id=2), 'Make sure to take your {} birth control pill and input notes, Constance.'.format(weekdays[timezone.now().weekday()]))
