def get_uuid():
    filename = "%s" % (uuid.uuid4())
    return filename

# birthing middleware
def process_user_request(ip, user_id, user_is_authenticated, path, content_length, http_referrer, querystring, method, index):
    from django.utils import timezone
    from django.contrib.auth.models import User
    import traceback
    import uuid, re
    import datetime
    import json
    from django.contrib.sessions.models import Session as SecureSession
    from security.models import Session, UserIpAddress
    from stacktrace.models import Error
    from uuid import UUID
    from django.conf import settings
    from security.apis import check_ip_risk
    user = User.objects.get(id=user_id) if user_is_authenticated else None
    RISK_LEVEL = 1
    FRAUD_MOD = settings.PAGE_LOADS_PER_API_CALL
    response = None
    try:
        k = str(uuid.uuid4())
        s = Session.objects.create(user=user if user_is_authenticated else None, ip_address=ip, path=path, content_length=content_length, http_referrer=http_referrer, uuid_key=k, injection_key=str(uuid.uuid4()), querystring=querystring, method=method, index=index)
        ip_obj = None
        if user_is_authenticated:
            ip_obj = user.security_profile.ip_addresses.filter(ip_address=ip).first()
            if ip_obj:
                ip_obj.timestamp = timezone.now()
                if not ip_obj.latitude:
                    from lotteh.celery import async_geolocation
                    async_geolocation.delay(ip_obj.id, ip)
                ip_obj.save()
        else:
            ip_obj = UserIpAddress.objects.filter(ip_address=ip, user=user if user_is_authenticated else None).first()
            if ip_obj:
                ip_obj.timestamp = timezone.now()
                if not ip_obj.latitude:
                    from lotteh.celery import async_geolocation
                    async_geolocation.delay(ip_obj.id, ip)
                ip_obj.save()
        if not ip_obj:
            ip_address = UserIpAddress()
            ip_address.user = user if user_is_authenticated else None
            from lotteh.celery import async_geolocation
            ip_address.ip_address = ip
            ip_address.timestamp = timezone.now()
            ip_address.save()
            async_geolocation.delay(ip_address.id, ip)
            ip_address.page_loads = 1
            from lotteh.celery import async_risk_detection
            ip_address.risk_detected = check_ip_risk(ip_address)
            if ip_address.risk_detected: ip_address.risk_count += 1
            ip_address.save()
            if user_is_authenticated:
                pr = user.security_profile
                pr.ip_addresses.add(ip_address)
                pr.save()
        else:
            ip_address.page_loads += 1
            ip_address.save()
            if ip_address.page_loads == FRAUD_MOD:
                if ip_address.risk_detected: pass
                else:
                    ip_address.risk_detected = check_ip_risk(ip_address)
                    if ip_address.risk_detected:
                        ip_address.risk_count += 1
                    ip_address.save()

    except:
        try:
            Error.objects.create(user=user if user_is_authenticated else None, stack_trace=traceback.format_exc(), notes='Logged by security middleware.')
        except: pass
#        set_current_exception(traceback.format_exc())
        print(traceback.format_exc())
#    response = get_response(request)
    return response
