from django.utils import timezone
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.contrib import messages
from users.models import Profile
from django.shortcuts import redirect
import urllib, json
import urllib.request
from django.contrib.auth.models import User
from .models import SecurityProfile, UserIpAddress, Session
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout
import traceback
import uuid, re
import datetime
from feed.middleware import set_current_exception
import requests
from requests.auth import HTTPBasicAuth
import json
from django.urls import reverse
from kick.views import is_kick
from django.contrib.sessions.models import Session as SecureSession
from security.apis import get_client_ip, check_ip_risk
from stacktrace.models import Error
from uuid import UUID
from django.conf import settings
from feed.middleware import get_current_exception

RISK_LEVEL = 1
FRAUD_MOD = settings.PAGE_LOADS_PER_API_CALL

class DummyRequest():
    ip = None
    user = None
    def __init__(self, reqlist):
        self.ip = reqlist[0]
        self.user = reqlist[1]
        return self

def get_request(reqlist):
    return DummyRequest(reqlist)

def fraud_detect(request, hard=False, dummy=False):
    if isinstance(request, list): request = get_request(request)
    if dummy: return False
    risk_detected = None
    try:
        ip = get_client_ip(request) if not hasattr(request, 'dummy') else request.ip
        if is_kick(ip, request.user) and hasattr(request, 'path') and not request.path.startswith("/kick/") and not request.path.startswith('/appeal/'):
            try:
                logout(request)
            except: pass
            user = None
        if hasattr(request.user, 'security_profile'):
            p = request.user.security_profile
            if not ip in request.user.security_profile.ip_addresses.values_list('ip_address', flat=True):
                ip_address = UserIpAddress()
                ip_address.user = request.user
                ip_address.ip_address = ip
                ip_address.save()
                ip_address.page_loads = 1
                ip_address.risk_detected = check_ip_risk(ip_address, soft=not hard)
                ip_address.save()
                p.ip_addresses.add(ip_address)
                p.save()
                if p.ip_addresses.count() % 10 == 0:
                    p = request.user.profile
                    p.identity_verified = False
                    p.save()
            p = request.user.profile
            if request.user.security_profile.ip_addresses.count() > 1 and not request.method == 'POST':
                messages.warning(request, 'You are using a new IP. Please verify your identity.')
                p.identity_confirmed = False
                p.save()
#                request.GET._mutable = True
#                request.GET.next = request.path
            ip_obj = request.user.security_profile.ip_addresses.filter(ip_address=ip).first()
            risk_detected = ip_obj.risk_detected
            if risk_detected or risk_detected == None:
                p.identity_verified = False
                p.identity_verification_failed = True
                p.save()
                messages.warning(request, 'You are using a suspicious IP. You have been logged out of the server.')
                print('Suspicious ID detected before API call')
                logout(request)
            if ip_obj.page_loads % FRAUD_MOD == 0 or hard:
                ip_obj.risk_detected = check_ip_risk(ip_obj, soft=not hard)
                ip_obj.save()
            ip_obj.page_loads = ip_obj.page_loads + 1
            ip_obj.save()
            risk_detected = ip_obj.risk_detected
            if risk_detected or risk_detected == None:
                p.identity_verified = False
                p.identity_verification_failed = True
                p.save()
                messages.warning(request, 'You are using a suspicious IP. You have been logged out of the server.')
                print('Suspicious ID detected after API call')
                logout(request)
    except:
        Error.objects.create(user=request.user if request.user.is_authenticated else None, stack_trace=get_current_exception(), notes='Logged by security middleware.')
        set_current_exception(traceback.format_exc())
        print(traceback.format_exc())
    return risk_detected
