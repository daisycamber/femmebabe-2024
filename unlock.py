import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lotteh.settings')
from django.conf import settings
settings.configure()
from django import db
db.connections.close_all()
