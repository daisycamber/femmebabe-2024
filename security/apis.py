import traceback
import requests
import json
from .models import UserIpAddress
from requests.auth import HTTPBasicAuth
from django.conf import settings
import ipaddress

HACKERGUARDIAN_RANGES = [] # ['64.39.96.0/20', '139.87.112.0/23']

FRAUDGUARD_USER = settings.FRAUDGUARD_USER
FRAUDGUARD_SECRET = settings.FRAUDGUARD_SECRET
ANTIDEO_KEY = settings.ANTIDEO_KEY

RISK_LEVEL = 1

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def ip_in_range(ip_addr):
    for range in HACKERGUARDIAN_RANGES:
        if ipaddress.ip_address(ip_addr) in ipaddress.ip_network(range): return True
    return False

def check_ip_risk(ip_addr, soft=False, dummy=True, guard=True):
    if dummy: return False
    if ip_in_range(ip_addr.ip_address): return False
    if not guard:
        try:
            ip=requests.get('https://api.antideo.com/ip/health/' + ip_addr.ip_address + '&apiKey={}'.format(ANTIDEO_KEY))
    #, verify=True, auth=HTTPBasicAuth(FRAUDGUARD_USER, FRAUDGUARD_SECRET))
            print(ip)
            j = ip.json()
            if j and j['health']['toxic'] or j['health']['spam']:
                return True
            else:
                return False
        except:
            print(traceback.format_exc())
            return not soft
    try:
        ip=requests.get('https://api.fraudguard.io/v2/ip/' + ip_addr.ip_address, verify=True, auth=HTTPBasicAuth(FRAUDGUARD_USER, FRAUDGUARD_SECRET))
        ip_addr.fraudguard_data = ip
        ip_addr.save()
        j = ip.json()
        if int(j['risk_level']) > RISK_LEVEL:
            if not soft:
                ip_addr.risk_detected = True
                ip_addr.risk_recheck = False
                ip_addr.save()
            return True
        else:
            ip_addr.risk_detected = False
            ip_addr.risk_recheck = False
            ip_addr.save()
            return False
    except:
        print(traceback.format_exc())
        return not soft
    return False

def check_raw_ip_risk(ip_address, soft=False, dummy=True, guard=True):
    if dummy: return False
    if ip_in_range(ip_address): return False
    if not guard:
        try:
            ip=requests.get('https://api.antideo.com/ip/health/' + ip_address + '&apiKey={}'.format(ANTIDEO_KEY))
    #, verify=True, auth=HTTPBasicAuth(FRAUDGUARD_USER, FRAUDGUARD_SECRET))
            print(ip)
            j = ip.json()
            if j and j['health']['toxic'] or j['health']['spam']:
                return True
            else:
                return False
        except:
            print(traceback.format_exc())
            return not soft
    try:
        ip=requests.get('https://api.fraudguard.io/v2/ip/' + ip_address, verify=True, auth=HTTPBasicAuth(FRAUDGUARD_USER, FRAUDGUARD_SECRET))
        print(ip)
        j = ip.json()
        if int(j['risk_level']) > RISK_LEVEL:
            return True
        else:
            return False
    except:
        print(traceback.format_exc())
        return not soft
    return False

def get_location(ip):
    try:
        response = requests.get('http://ipinfo.io/' + ip + '?token=490ce4335d8800').json()
        city = response['city']
        region = response['region']
        country = response['country']
        org = response['org']
        return '{}, {}, {} - {}'.format(city, region, country, org)
    except: return ''
