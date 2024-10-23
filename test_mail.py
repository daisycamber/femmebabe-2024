import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lotteh.settings')

import django
django.setup()
from users.email import send_email
import sys
email = sys.argv[1]
send_email(email, 'This is a test subject', 'I am testing the mail server to make sure it works. This is just a test of the mail server. I want to make sure I can send email prroperly using the web app.')
