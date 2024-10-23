from verify.forms import get_past_date
from datetime import datetime
from django.utils import timezone
from django.conf import settings
import pytz, re

tz = pytz.timezone(settings.TIME_ZONE)

def text_has_valid_expiry(image_text, seperator='/'):
    expiry_valid = False
    matches = []
    if seperator == '/':
        matches = re.findall('[\d+]+/[\d+]+/[\d+]+'.format(seperator, seperator), image_text)
        if len(matches) < 2:
            matches = re.findall('[\d+]+-[\d+]+-[\d+]+'.format(seperator, seperator), image_text)
    else:
        matches = re.findall('[0-9][0-9][0-9][0-9][1-2][0-9][0-9][0-9]', image_text)
    s = seperator
    expiry = None
    for match in matches:
        print(match)
        if seperator == '' and not len(match) == 8:
            continue
        if seperator == '':
            match = match[0:2] + s + match[2:4] + s + match[4:8]
        date_on_id = None
        try:
            date_on_id = datetime.strptime(match, '%m{}%d{}%Y'.format(s,s)).replace(tzinfo=tz)
        except:
            try:
                date_on_id = datetime.strptime(match, '%d{}%m{}%Y'.format(s,s)).replace(tzinfo=tz)
            except:
                pass
        if not date_on_id: continue
        print(str(date_on_id))
        if date_on_id > timezone.now().replace(tzinfo=tz):
            expiry_valid = True
            expiry = date_on_id
    if expiry_valid:
        return expiry
    return False

def text_has_valid_birthday_and_expiry(image_text, seperator='/'):
    bday_valid = False
    expiry_valid = False
    matches = []
    if seperator == '/':
        matches = re.findall('[\d+]+/[\d+]+/[\d+]+'.format(seperator, seperator), image_text)
        if len(matches) < 2:
            matches = re.findall('[\d+]+-[\d+]+-[\d+]+'.format(seperator, seperator), image_text)
    else:
        matches = re.findall('[0-9][0-9][0-9][0-9][1-2][0-9][0-9][0-9]', image_text)
    s = seperator
    bday = None
    expiry = None
    bday = get_past_date().replace(tzinfo=tz)
    for match in matches:
        print(match)
        if seperator == '' and not len(match) == 8:
            continue
        if seperator == '':
            match = match[0:2] + s + match[2:4] + s + match[4:8]
        date_on_id = None
        try:
            date_on_id = datetime.strptime(match, '%m{}%d{}%Y'.format(s,s)).replace(tzinfo=tz)
        except:
            try:
                date_on_id = datetime.strptime(match, '%d{}%m{}%Y'.format(s,s)).replace(tzinfo=tz)
            except:
                pass
        if not date_on_id: continue
        print(str(date_on_id))
        if date_on_id < bday:
            bday_valid = True
            bday = date_on_id
        if date_on_id > timezone.now().replace(tzinfo=tz):
            expiry_valid = True
            expiry = date_on_id
    if bday_valid and expiry_valid:
        return (bday, expiry)
    return False

def text_matches_name(image_text, name):
    split = name.lower().split(" ")
    image_text = image_text.lower()
    for text in split:
        if not text in image_text:
            print("Id name mismatch " + name + " " + image_text)
            return False
    print('ID name matches')
    return True

def text_matches_birthday(image_text, birthday):
    if not birthday in image_text:
        print("Id birthday mismatch " + birthday)
        return False
    return True
