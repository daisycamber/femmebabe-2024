EMAIL_AFTER_DAYS = 3

def send_retargeting_email():
    from users.email import send_html_email
    from django.contrib.auth.models import User
    from django.utils import timezone
    from datetime import timedelta
    from django.conf import settings
    from django.template.loader import render_to_string
    from pwa_webpush import send_group_notification
    from users.tfa import send_user_text
    from feed.models import Post

    posts = Post.objects.filter(author__id=settings.MY_ID, enhanced=True, private=False, public=True, published=True, recipient=None).exclude(image=None).order_by('-date_posted').values_list('id', flat=True)[:settings.FREE_POSTS]
    post = Post.objects.filter(id__in=posts).exclude(image_offsite=None).order_by('?').first()
    photo_url = post.image_offsite
    days = 3
    for user in User.objects.filter(is_active=True, profile__email_verified=True, profile__subscribed=True):
        html_message = render_to_string('retargeting/routine_retargeting_email.html', {
            'site_name': settings.SITE_NAME,
            'user': user,
            'domain': settings.DOMAIN,
            'protocol': 'https',
            'photo': photo_url,
        })
        send_html_email(user, 'Visit {}, {}'.format(settings.SITE_NAME, user.username), html_message)

def send_retargeting_emails():
    from users.email import send_html_email
    from django.contrib.auth.models import User
    from django.utils import timezone
    from datetime import timedelta
    from django.conf import settings
    from django.template.loader import render_to_string
    from pwa_webpush import send_group_notification
    from users.tfa import send_user_text
    from feed.models import Post

    posts = Post.objects.filter(author__id=settings.MY_ID, enhanced=True, private=False, public=True, published=True, recipient=None).exclude(image=None).order_by('-date_posted').values_list('id', flat=True)[:settings.FREE_POSTS]
    post = Post.objects.filter(id__in=posts).exclude(image_offsite=None).order_by('?').first()
    photo_url = post.image_offsite
    days = 3
    for user in User.objects.filter(is_active=True, profile__email_verified=True, profile__date_joined__lte=timezone.now() - timedelta(hours=24*days), profile__date_joined__gte=timezone.now() - timedelta(hours=24*(days+1)), profile__subscribed=True):
        html_message = render_to_string('retargeting/retargeting_email.html', {
            'site_name': settings.SITE_NAME,
            'user': user,
            'domain': settings.DOMAIN,
            'protocol': 'https',
            'photo': photo_url,
        })
        send_html_email(user, 'Come back to {}, {}'.format(settings.SITE_NAME, user.username), html_message)
    days = 7
    for user in User.objects.filter(profile__date_joined__lte=timezone.now() - timedelta(hours=24*days), profile__date_joined__gte=timezone.now() - timedelta(hours=24*(days+1)), profile__subscribed=True):
        html_message = render_to_string('retargeting/retargeting_email_2.html', {
            'site_name': settings.SITE_NAME,
            'user': user,
            'domain': settings.DOMAIN,
            'protocol': 'https',
            'photo': photo_url,
        })
        send_html_email(user, 'It\'s been a while, {}. Visit {}'.format(user.username, settings.SITE_NAME), html_message)
    days = 14
    for user in User.objects.filter(profile__date_joined__lte=timezone.now() - timedelta(hours=24*days), profile__date_joined__gte=timezone.now() - timedelta(hours=24*(days+1)), profile__subscribed=True):
        if user.profile.phone_number:
            send_user_text(user, 'Hey {}, do you have some time to visit {}? Spend some time with me and consider subscribing, buying a photo, or leaving a tip. I\'ll be waiting! Visit {}'.format(user.username, settings.SITE_NAME, settings.BASE_URL))
    days = 21
    for user in User.objects.filter(profile__date_joined__lte=timezone.now() - timedelta(hours=24*days), profile__date_joined__gte=timezone.now() - timedelta(hours=24*(days+1)), profile__subscribed=True):
        if user.profile.phone_number:
            send_user_text(user, 'Hey {}, it\'s been three weeks since you joined me on {}. Want to come back and see what\'s new? Visit {}'.format(user.username, settings.SITE_NAME, settings.BASE_URL))
    days = 30
    for user in User.objects.filter(profile__date_joined__lte=timezone.now() - timedelta(hours=24*days), profile__date_joined__gte=timezone.now() - timedelta(hours=24*(days+1)), profile__subscribed=True):
        html_message = render_to_string('retargeting/retargeting_email_3.html', {
            'site_name': settings.SITE_NAME,
            'user': user,
            'domain': settings.DOMAIN,
            'protocol': 'https',
            'photo': photo_url,
        })
        send_html_email(user, 'It would be great to have you back, {}. Go visit {}'.format(user.username, settings.SITE_NAME), html_message)
