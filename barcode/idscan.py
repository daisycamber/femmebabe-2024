import requests
import json
from django.conf import settings
import base64
import codecs
from io import BytesIO
from PIL import Image
from verify.forms import get_past_date
from datetime import datetime
from django.utils import timezone
import pytz
from .models import DocumentScan

utc=pytz.timezone(settings.TIME_ZONE)
#pytz.UTC

def scan_id(scan_path, instance):
    api_url = "https://app1.idware.net/DriverLicenseParserRest.svc/ParseImage"
    with open(scan_path, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
    todo = {"authKey": settings.IDSCAN_AUTH_KEY, "data": encoded_string}
    headers =  {"Content-Type":"text/json", "Cache-Control": "no-cache"}
    response = requests.post(api_url, data=json.dumps(todo), headers=headers)
    decoded_data=codecs.decode(response.text.encode(), 'utf-8-sig')
    instance.idscan = str(decoded_data)
    instance.save()
    print(instance.idscan)
    response = json.loads(instance.idscan)
    prev_scan = DocumentScan.objects.filter(idscan=idscan).last()
    if prev_scan and verification and prev_scan.user != verification.user:
        messages.warning(request, 'ID validation failed due to pre existing ID scan with name ' + prev_scan.user.username)
        return False
    result = response['ParseImageResult']
    document = result[list(result.keys())[0]]
    exp_date = document['ExpirationDate']
    exp_date = datetime.strptime(exp_date, '%Y-%m-%d').replace(tzinfo=utc)
    if exp_date < timezone.now().date():
        return False
    birthday = document['Birthdate']
    birthday = datetime.strptime(birthday, '%Y-%m-%d').replace(tzinfo=utc)
    if birthday > get_past_date().replace(tzinfo=utc):
        return False
    if result['Success'] and int(result['Confidence']) > settings.MIN_CONFIDENCE:
        instance.verified = True
        instance.save()
        return True
    return False

