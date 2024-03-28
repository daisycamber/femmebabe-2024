from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from feed.models import Post
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test
from feed.tests import identity_verified
from vendors.tests import is_vendor
from django.http import HttpResponse
from feed.templatetags.app_filters import nts, stime, ampm
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from misc.regex import SEARCH_REGEX
from misc.regex import ESCAPED_QUERIES
import regex
from django.views.decorators.csrf import csrf_exempt
import datetime
from feed.models import Post

def adstxt(request):
    return render(request, 'ads.txt')

def sitemap(request):
    from .sitemap import urls
    from .sitemap import vendor_urls
    from .sitemap import languages
    return render(request, 'misc/sitemap.xml', {'posts': Post.objects.filter(public=True, private=False, published=True).exclude(content=''), 'vendors': User.objects.filter(profile__vendor=True, is_active=True), 'vendor_urls': vendor_urls, 'urls': urls, 'languages': languages, 'base_url': settings.BASE_URL, 'date': timezone.now().strftime('%Y-%m-%d')}, content_type='application/xml')

def news(request):
    from .sitemap import languages
    languages = ['en']
    urls = ['/landing/', '/about/', '/accounts/login/', '/accounts/register/', '/']
    vendor_urls = ['/feed/grid/', '/feed/profile/', '/payments/photo/', '/payments/subscribe/', '/payments/crypto/']
    surrogate_urls = ['/surrogacy/', '/surrogacy/checkout/']
    return render(request, 'misc/news.xml', {'profiles': User.objects.filter(is_active=True, profile__vendor=True), 'surrogates': User.objects.filter(is_active=True, profile__vendor=True, vendor_profile__activate_surrogacy=True), 'posts': Post.objects.filter(public=True, private=False, published=True).exclude(content=''), 'languages': languages, 'base_url': settings.BASE_URL, 'date': timezone.now().strftime('%Y-%m-%d'), 'urls': urls, 'vendor_urls': vendor_urls, 'surrogate_urls': surrogate_urls}, content_type='application/xml')

def idscan(request):
    return render(request, 'misc/idscan.html')

def ad(request):
    return render(request, 'ad_frame.html', {'hidenavbar': True, 'load_timeout': 0})

def verify(request):
    return HttpResponse('f7fcf64bfb499980d251f6ffb6676460')

def current_time(now):
    resp = '{} {}'.format(stime(now).capitalize(), ampm(now))
    return resp

def time(request):
    resp = current_time()
    return HttpResponse(resp)

@csrf_exempt
def authenticated(request):
    return HttpResponse('y' if request.user.is_authenticated else 'n')

def terms(request):
    return render(request, 'misc/terms.html', {
        'title': 'Terms and Conditions',
        'city_state': settings.CITY_STATE,
        'address': settings.ADDRESS,
        'phone_number': settings.PHONE_NUMBER,
        'email_address': settings.EMAIL_ADDRESS,
        'agent_name': settings.AGENT_NAME,
    })

def privacy(request):
    return render(request, 'misc/privacy.html', {'title': 'Privacy'})

def get_posts_for_query(request, qs):
    now = timezone.now()
    try:
        now = datetime.datetime.fromtimestamp(int(request.GET.get('time')) / 1000)
    except: pass
    from autocorrect import Speller
    from translate.translate import translate
    spell = Speller()
    qs = spell(qs)
    qs = translate(request, qs, target=settings.DEFAULT_LANG)
    qsplit = qs.split(' ')
    posts = Post.objects.filter(content__icontains=qs, private=False, published=True, date_posted__lte=now)
    for q in qsplit:
        posts = posts.union(Post.objects.filter(content__icontains=q, private=False, published=True, date_posted__lte=now))
    posts = posts.order_by('-date_posted')
    pos = []
    for post in posts:
        count = 0
        matches = regex.findall(SEARCH_REGEX.format(qs), post.content, flags=regex.IGNORECASE | regex.BESTMATCH)
        count = count + len(matches) * len(qsplit)
        for q in qsplit:
            matches = regex.findall(SEARCH_REGEX.format(q), post.content, flags=regex.IGNORECASE | regex.BESTMATCH)
            for match in matches:
                if not match in ESCAPED_QUERIES:
                    count = count + 1
        if count > 0:
            pos = pos + [(post.id, count)]
    pos = sorted(pos, key = lambda x: x[1], reverse=True)
    posts = []
    for post, count in pos:
        post = Post.objects.get(id=post)
        posts = posts + ([post] if post.public or request.user.is_authenticated and post.author in request.user.profile.subscriptions.all() or request.user.is_authenticated and request.user.profile.vendor else [])
    return posts

#@login_required
#@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def search(request):
    page = 1
    if(request.GET.get('page', None) != None):
        page = int(request.GET.get('page'))
    qs = request.GET.get('q',None)
    if not qs:
        messages.warning(request, "Please enter a valid querystring to search {}".format(settings.SITE_NAME))
        qs = ''
    posts = get_posts_for_query(request, qs)
    p = Paginator(posts, 10)
    if page > p.num_pages or page < 1:
        messages.warning(request, "The page you requested, " + str(page) + ", does not exist. You have been redirected to the first page.")
        page = 1
    template_name = 'misc/search.html'
    if request.GET.get('grid'):
        template_name = 'feed/profile_grid.html'
    return render(request, template_name, {
        'title': 'Search {}'.format(settings.SITE_NAME),
        'posts': p.page(page),
        'count': p.count,
        'page_obj': p.get_page(page),
        'query': request.GET.get('q', None),
        'full': request.GET.get('grid'),
    })

def robotstxt(request):
    return render(request, 'robots.txt')
