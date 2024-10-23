from users.email import send_html_email
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.template.loader import render_to_string
from barcode.models import DocumentScan
import json, datetime

def send_routine_email():
    for user in User.objects.filter(is_active=True, profile__idscan_active=True, profile__subscribed=True):
        scans = DocumentScan.objects.filter(user=user, foreign=True, timestamp__lte=timezone.now(), timestamp__gte=timezone.now() - datetime.timedelta(hours=24*32)).order_by('-timestamp')
        photo_urls = []
        for scan in scans:
            number = None
            name = None
            try:
                data = json.load(verification.idscan)
                result = data['ParseResult']
                document = result[list(result.keys())[0]]
                number = document['LicenseNumber'] if 'LicenseNumber' in document else document['IDNumber']
                name = document['FullName']
            except: pass
            photo_urls = photo_urls = [{'idscan': scan.idscan, 'data': scan.barcode_data, 'name': name, 'number': number}]
        html_message = render_to_string('barcode/routine_email.html', {
            'site_name': settings.SITE_NAME,
            'user': user,
            'domain': settings.DOMAIN,
            'protocol': 'https',
            'photo_urls': photo_urls,
        })
        send_html_email(user, 'Your ID Scanner Digest from {}, {}'.format(settings.SITE_NAME, user.username), html_message)
