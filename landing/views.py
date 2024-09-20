from django.views.decorators.vary import vary_on_cookie
from django.views.decorators.cache import patch_cache_control
from django.views.decorators.cache import cache_page

@cache_page(60*60*24*30*12)
def landing(request):
    from django.shortcuts import render
    from django.contrib.auth.decorators import login_required
    from django.urls import reverse
    from django.shortcuts import redirect
    from users.models import get_user_count
    from feed.models import Post
    from live.models import VideoRecording
    from security.apis import get_client_ip, get_location, check_raw_ip_risk
    from security.models import UserIpAddress
    from django.contrib import messages
    from django.conf import settings
    from audio.models import AudioRecording
    from django.contrib.auth.models import User
    from interactive.models import Choices
    from security.models import UserIpAddress
    from contact.forms import ContactForm
    from feed.templatetags.app_filters import clean_html
    ip = get_client_ip(request)
#    if not request.user.is_authenticated and check_raw_ip_risk(ip):
#        messages.warning(request, 'You are using a suspicious IP. You should refer to the terms and make sure to follow them before visiting the site. Thank you.')
#        return redirect(reverse('misc:terms'))
#    if UserIpAddress.objects.filter(ip_address=ip, user=None).count() == 0 and not request.GET.get('k', None):
#        return redirect(reverse('feed:profile-grid', kwargs={'username': User.objects.filter(id=settings.MY_ID).first().profile.name}))
    loc = None
    loc = (get_location(ip))
    post = Post.objects.filter(id=settings.SPLASH).first()
    me = User.objects.filter(id=settings.MY_ID).first()
    my_name = 'Daisy'
    if me: my_name = me.profile.name
    posts = Post.objects.filter(pinned=True, published=True, private=False, public=True).exclude(image=None).order_by('?')[:6]
    if posts.count() < 6: posts = Post.objects.filter(published=True, private=False, public=True).exclude(image=None).order_by('?')[:6]
    posts1 = posts[:3]
    posts2 = posts[3:]
    return render(request, 'landing/landing.html', {
        'users': get_user_count(),
        'preload': True,
        'my_name': my_name,
        'my_photo': me.profile.get_image_url(),
        'post_count': Post.objects.filter(private=False).count(),
        'photo_count': Post.objects.filter(private=False).exclude(image=None).count(),
        'recording_count': VideoRecording.objects.filter(public=True, processed=True, camera='private').count(),
        'audio_count': AudioRecording.objects.filter(public=True).count(),
        'interactive_count': Choices.objects.all().exclude(label='idle').count(),
        'location': loc,
        'splash': clean_html(post.content) if post else 'Welcome.\nTap or click the screen to continue.',
        'company_name': settings.COMPANY_NAME,
        'ubi': settings.UBI,
        'posts1': posts1,
        'posts2': posts2,
        'profile': me.profile,
    })

@cache_page(60*60*24*30*12)
def index(request):
    import datetime
    from django.conf import settings
    from django.shortcuts import render
    from django.contrib.auth.decorators import login_required
    from django.urls import reverse
    from django.shortcuts import redirect
    from django.http import HttpResponseRedirect
    if request.method == 'GET' and request.path == '/' and not request.GET.get('k') and not request.META.get('HTTP_REFERRER'):
        if request.user.is_authenticated and request.user.profile.vendor:
            return redirect(reverse('go:go'))
        elif not request.COOKIES.get('return_visit'):
            max_age = settings.LANDING_COOKIE_EXPIRATION_DAYS * 24 * 60 * 60
            expires = datetime.datetime.strftime(
                datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
                "%a, %d-%b-%Y %H:%M:%S GMT",
            )
            response = HttpResponseRedirect(reverse('landing:index'))
            response.set_cookie('return_visit', True, max_age=max_age, expires=expires)
            return response
    from users.models import get_user_count
    from feed.models import Post
    from live.models import VideoRecording
    from security.apis import get_client_ip, get_location, check_raw_ip_risk
    from security.models import UserIpAddress
    from django.contrib import messages
    from django.conf import settings
    from audio.models import AudioRecording
    from django.contrib.auth.models import User
    from interactive.models import Choices
    from security.models import UserIpAddress
    from contact.forms import ContactForm
    posts = Post.objects.filter(pinned=True, published=True, private=False, public=True).exclude(image=None).order_by('?')[:3]
    if posts.count() < 3: posts = Post.objects.filter(published=True, private=False, public=True).exclude(image=None).order_by('?')[:3]
    me = User.objects.filter(id=settings.MY_ID).first()
    response = render(request, 'landing/index.html', {'title': 'Landing', 'darkmode': False, 'description': 'We can help your business get online and grow, fast. Buy a custom app solution, ID scanning services, or subscribe to the photo/video blog with live video.', 'hidenavbar': True, 'profile': me.profile, 'posts1': posts, 'github_url': settings.GITHUB_URL, 'resume_url': settings.RESUME_URL, 'linkedin_url': settings.LINKEDIN_URL, 'twitter_url': settings.TWITTER_LINK, 'contact_form': ContactForm()})
    return response
