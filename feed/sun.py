from datetime import datetime, time, date, timedelta
from django.conf import settings
from django.contrib.auth.models import User
import pytz, traceback, random, os
from security.models import Session as SecureSession
from feed.models import Post
from security.models import UserIpAddress, UserSession
from security.apis import get_client_ip
from misc.views import current_time
from django.utils import timezone
from security.tests import face_mrz_or_nfc_verified
from django.contrib.auth.models import User

def utc_to_local(utc_dt, local_tz):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)

def get_sun(user_id, user_is_authenticated, ip):
    if user_is_authenticated:
        user = User.objects.get(id=user_id)
        ip = UserIpAddress.objects.filter(user=None if not user_is_authenticated else user, ip_address=ip).first()
        if ip != None and ip.latitude != None and ip.longitude != None:
            from astral.sun import sun
            from astral import LocationInfo
            from astral.location import Location
            from dateutil.parser import parse
            location = LocationInfo(latitude=ip.latitude, longitude=ip.longitude)
            loc = Location(location)
            timezone_str = 'America/Los Angeles'
            if not ip.timezone:
                import timezonefinder
                tf = timezonefinder.TimezoneFinder()
                timezone_str = tf.certain_timezone_at(lat=ip.latitude, lng=ip.longitude)
                ip.timezone = timezone_str
                ip.save()
            else: timezone_str = ip.timezone
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)
            s = sun(location.observer, date=now.date(), tzinfo=timezone_str)
            sunrise = parse(f'{s["sunrise"]}').astimezone(tz)
            sunset = parse(f'{s["sunset"]}').astimezone(tz)
            ip.sunset = sunset
            ip.sunrise = sunrise
            ip.last_updated_sun = timezone.now()
            ip.save()
