use_bs4 = False

from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test
from .tests import identity_verified
from vendors.tests import is_vendor
from barcode.tests import document_scanned
from django.views.decorators.cache import patch_cache_control
from django.views.decorators.vary import vary_on_cookie
from django.views.generic import (
    UpdateView,
    DeleteView
)
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache, cache_page
from security.security import fraud_detect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

basedescription = '{} is an app for adults.'.format(settings.SITE_NAME)

def sub_fee(fee):
    import math
    op = ''
    of = len(str(fee))%3
    op = op + str(fee)[0:of] + (',' if of > 0 else '')
    for f in range(math.floor(len(str(fee))/3)):
        op = op + str(fee)[3*f+of:3+3*f+of] + ','
    op = op[:-1]
    return op

def report_alert(post, report_text):
    from django.contrib.auth.models import User
    recipient = User.objects.filter(id=settings.MY_ID).first()
    from feed.templatetags.app_filters import shorttitle
    from django.urls import reverse
    payload = {'head': 'The post, {} by {}, has been reported.'.format(shorttitle(post.id), post.author.profile.name), 'body': 'The report included the following content: {}'.format(report_text), 'icon': '{}{}'.format(settings.BASE_URL, settings.ICON_URL), 'url': settings.BASE_URL + reverse('feed:post-detail', kwargs={'uuid': post.get_friendly_name()})}
    from pwa_webpush import send_user_notification
    try:
        send_user_notification(recipient, payload=payload)
    except: pass


@csrf_exempt
def report(request, uid):
    from django.http import HttpResponse
    if request.method == 'POST':
        from .forms import ReportForm
        form = ReportForm(request.POST)
        p = Post.objects.get(uuid=uid)
        user = request.user if request.user.is_authenticated else None
        if form.is_valid():
            form.instance.user = user
            form.instance.post = p
            report = form.save()
            if report.post.reports.count() > settings.REPORTS_TO_HIDE:
                p.safe = False
                p.save()
            report_alert(report.post, report.text)
            return HttpResponse('Your report was received. Thank you for your report.')
    return HttpResponse('Your report was invalid. Please try again.')

@csrf_exempt
def auction(request, id):
    import traceback
    from feed.models import Post
    from django.shortcuts import render
    from .forms import BidForm, UserBidForm
    from django.shortcuts import get_object_or_404, render, redirect
    from django.urls import reverse
    from django.contrib import messages
    from django.http import HttpResponse
    from django.conf import settings
    from django.core.paginator import Paginator
    import traceback
    from django.contrib.auth.models import User
    from users.email import send_verification_email
    from users.models import Profile
    from security.models import SecurityProfile
    from users.username_generator import generate_username as get_random_username
    from django.utils.crypto import get_random_string
    from contact.email import send_contact_confirmation
    from security.apis import get_client_ip
    from security.apis import check_raw_ip_risk
    from django.conf import settings
    from users.email import sendwelcomeemail
    post = get_object_or_404(Post, friendly_name=id)
    if request.method == 'POST':
        form = UserBidForm(request.POST) if request.user.is_authenticated else BidForm(request.POST)
        if form.is_valid():
            ip = get_client_ip(request)
            e = form.cleaned_data.get('email', None) if not request.user.is_authenticated else request.user.email
            from email_validator import validate_email
            valid = validate_email(e, check_deliverability=True)
            us = User.objects.filter(email=e).last()
            safe = not check_raw_ip_risk(ip, soft=True, dummy=False, guard=True)
            if valid and (not us) and safe:
                user = User.objects.create_user(email=e, username=get_random_username(), password=get_random_string(length=8))
                if not hasattr(user, 'profile'):
                    profile = Profile.objects.create(user=user)
                    profile.finished_signup = False
                    profile.save()
                    security_profile = SecurityProfile.objects.create(user=user)
                    security_profile.save()
                send_verification_email(user)
                sendwelcomeemail(user)
            elif not valid:
                messages.warning(request, 'Invalid or undeliverable email, please check the email and try again')
                return render(request, 'feed/bid.html', {'title': 'Auction', 'form': UserBidForm(post.bids.last().bid if post.bids.count() else settings.MIN_BID + 1, initial={'bid': settings.MIN_BID + 1 if not post.bids.count() else post.bids.last() + 1}) if request.user.is_authenticated else BidForm(post.bids.last().bid if post.bids.count() else settings.MIN_BID + 1, initial={'bid': settings.MIN_BID + 1 if not post.bids.count() else post.bids.last() + 1}), 'current_bid': post.bids.last().bid if post.bids.count() else settings.MIN_BID, 'small': True, 'post': post})
            elif not safe:
                messages.warning(request, 'You are using a risky IP address, and your contact request has been denied.')
                return render(request, 'feed/bid.html', {'title': 'Auction', 'form': UserBidForm(post.bids.last().bid if post.bids.count() else settings.MIN_BID + 1, initial={'bid': settings.MIN_BID + 1 if not post.bids.count() else post.bids.last() + 1}) if request.user.is_authenticated else BidForm(post.bids.last().bid if post.bids.count() else settings.MIN_BID + 1, initial={'bid': settings.MIN_BID + 1 if not post.bids.count() else post.bids.last() + 1}), 'current_bid': post.bids.last().bid if post.bids.count() else settings.MIN_BID, 'small': True, 'post': post})
            us = User.objects.filter(email=e).last()
            try:
                if (post.bids.last().bid if post.bids.count() else settings.MIN_BID) < int(form.cleaned_data['bid']):
                    bid = form.save()
                    bid.user = us
                    bid.post = post
                    bid.save()
                    messages.success(request, 'Your bid has been placed.')
                else: messages.warning(request, 'Your bid is less than the current bid and could not be placed.')
            except:
                print(traceback.format_exc())
                messages.warning(request, 'Your bid failed.')
        else: messages.warning(request, str(form.errors))
    return render(request, 'feed/bid.html', {'title': 'Auction', 'form': UserBidForm(post.bids.last().bid if post.bids.count() else settings.MIN_BID + 1, initial={'bid': settings.MIN_BID + 1 if not post.bids.count() else post.bids.last() + 1}) if request.user.is_authenticated else BidForm(post.bids.last().bid if post.bids.count() else settings.MIN_BID + 1, initial={'bid': settings.MIN_BID + 1 if not post.bids.count() else post.bids.last() + 1}), 'current_bid': post.bids.last().bid if post.bids.count() else settings.MIN_BID, 'small': True, 'post': post})

@csrf_exempt
@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def like(request, uuid):
    from django.shortcuts import get_object_or_404
    from django.utils import timezone
    import datetime
    from feed.models import Post
    from django.http import HttpResponse
    post = get_object_or_404(Post, uuid=uuid, published=True)
    if request.method == 'POST' and request.user.profile.can_like < timezone.now() - datetime.timedelta(seconds=2):
        if post in request.user.profile.likes.all():
            request.user.profile.can_like = timezone.now()
            request.user.profile.likes.remove(post)
            request.user.profile.save()
            return HttpResponse('<i class="bi bi-arrow-through-heart"></i>')
        else:
            request.user.profile.can_like = timezone.now()
            request.user.profile.likes.add(post)
            request.user.profile.save()
            return HttpResponse('<i class="bi bi-arrow-through-heart-fill"></i>')
    return HttpResponse('<i class="bi bi-arrow-through-heart-fill"></i>' if post in request.user.profile.likes.all() else '<i class="bi bi-arrow-through-heart"></i>')

@csrf_exempt
@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def publish(request, pk):
    from django.shortcuts import get_object_or_404
    from feed.models import Post
    from django.utils import timezone
    import datetime
    from django.http import HttpResponse
    post = get_object_or_404(Post, id=pk)
    if request.method == 'POST' and post.author == request.user and request.user.profile.can_like < timezone.now() - datetime.timedelta(seconds=3):
        if post.private and post.public:
            post.private = True
            post.public = False
        elif not post.private and not post.public:
            post.private = False
            post.public = True
        elif post.private and not post.public:
            post.private = False
        elif post.public and not post.private:
            post.public = False
        post.save()
    request.user.profile.can_like = timezone.now()
    request.user.profile.save()
    return HttpResponse('{}/{}'.format('priv' if post.private else 'publ', 'publ' if post.public else 'priv'))

@csrf_exempt
@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def pin(request, pk):
    from django.shortcuts import get_object_or_404
    from django.utils import timezone
    import datetime
    from django.http import HttpResponse
    post = get_object_or_404(Post, id=pk)
    if request.method == 'POST' and post.author == request.user and request.user.profile.can_like < timezone.now() - datetime.timedelta(seconds=3):
        post.pinned = not post.pinned
        post.save()
    request.user.profile.can_like = timezone.now()
    request.user.profile.save()
    return HttpResponse('<i class="bi bi-pin-angle-fill"></i>' if post.pinned else '<i class="bi bi-pin-fill"></i>')

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def tip(request, username, tip):
    from django.shortcuts import redirect
    from django.urls import reverse
    return redirect(reverse('payments:tip-bitcoin', kwargs={'username': username, 'tip': tip}))

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def private(request, username):
    from users.models import Profile
    from feed.models import Post
    from django.shortcuts import get_object_or_404
    from django.utils import timezone
    import datetime
    from django.core.paginator import Paginator
    from django.contrib import messages
    from django.http import HttpResponse
    profile = get_object_or_404(Profile, name=username, vendor=True)
    page = 1
    if(request.GET.get('page', None) != None):
        page = int(request.GET.get('page', None))
    following = False
    posts = Post.objects.filter(author=profile.user, posted=False).union(Post.objects.filter(author=profile.user, private=True)).order_by('-date_posted')
    p = Paginator(posts, 10)
    if page > p.num_pages or page < 1:
        messages.warning(request, "The page you requested, " + str(page) + ", does not exist. You have been redirected to the first page.")
        page = 1
    return render(request, 'feed/private.html', {
        'title': '@' + profile.name + '\'s Private Posts',
        'posts': p.page(page),
        'count': p.count,
        'page_obj': p.get_page(page),
        'profile': profile,
        'following': following,
        'preload': True,
        'load_timeout': 6000
    })

def get_qs(rqg):
    qs = '?'
    for key, value in rqg.items():
        qs = qs + ('{}={}&'.format(key, value) if key != 'square' else '')
    return qs

def unique(list):
    unique_list = []
    for item in list:
        if not item in unique_list:
            unique_list.append(item)
    return unique_list

from translate.translate import translate

#@login_required
#@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@csrf_exempt
@cache_page(60*60*24*7)
@vary_on_cookie
def grid_api(request, index):
    from django.utils import timezone
    from security.middleware import get_qs
    from django.core.paginator import Paginator
    from misc.views import get_posts_for_query
    from itertools import chain
    import datetime
    from users.models import Profile
    import pytz
    from feed.models import Post
    from django.http import HttpResponse
    now = datetime.datetime.fromtimestamp(int(request.GET.get('time')) / 1000, tz=pytz.UTC)
    username = request.GET.get('name')
    profile = Profile.objects.filter(name=username, vendor=True).first()
    posts = None
    following = False
    post = None
    url = ''
    square = True if request.GET.get('square') else False
    likes = request.GET.get('likes')
    pins = None
    if likes and request.user.is_authenticated:
        posts = request.user.profile.likes.filter(posted=True, author=profile.user, private=False, published=True, recipient=None, date_posted__lte=now, feed=settings.DEFAULT_FEED).union(request.user.profile.likes.filter(author=profile.user, private=True, recipient=request.user, published=True, date_posted__lte=now, feed=settings.DEFAULT_FEED)).exclude(image=None, feed='blog').order_by('-date_posted')
        post = posts[index%len(posts)]
    elif not request.GET.get('q') and profile:
        if request.user.is_authenticated and (profile.user in request.user.profile.subscriptions.all() or (request.user == profile.user and request.GET.get('show', False))):
            following = True
            ids = Post.objects.filter(posted=True, author=profile.user, private=False, published=True, recipient=None, date_posted__lte=now, feed=settings.DEFAULT_FEED).exclude(image=None, feed='blog').order_by('-date_posted')
            pins = Post.objects.filter(posted=True, author=profile.user, private=False, public=True, pinned=True, recipient=None, published=True, date_posted__lte=now, feed=settings.DEFAULT_FEED).exclude(image=None, feed='blog').order_by('-date_posted')
            rec = Post.objects.filter(posted=True, author=profile.user, private=False, public=False, pinned=False, recipient=request.user if request.user.is_authenticated else None, published=True, date_posted__lte=now, feed=settings.DEFAULT_FEED).exclude(image=None, feed='blog').order_by('-date_posted') if request.user.is_authenticated else []
            if request.user.is_authenticated and document_scanned(request.user):
                ids = ids.union(Post.objects.filter(posted=True, author=profile.user, secure=True, private=True, public=False, pinned=False, published=True, date_posted__lte=now, feed=settings.DEFAULT_FEED).exclude(image=None, feed='blog').order_by('-date_posted') if request.user.is_authenticated else []).order_by('-date_posted')
            posts = unique(list(chain(pins, rec, ids)))
            post = posts[index%len(posts)]
            if not post.image: return HttpResponse('')
            if request.user == profile.user and post.public:
                url = post.get_image_url() if not square else post.get_image_thumb_url()
            elif (request.user == profile.user and not request.GET.get('show')) and not post.public:
                url = post.get_blur_url() if not square else post.get_blur_thumb_url()
            else:
                url = post.get_image_url() if not square else post.get_image_thumb_url()
        elif not request.GET.get('q'):
            ids = Post.objects.filter(posted=True, author=profile.user, public=True, private=False, published=True, recipient=None, date_posted__lte=now, feed=settings.DEFAULT_FEED).exclude(image=None, feed='blog').order_by('-date_posted')
            pins = Post.objects.filter(posted=True, author=profile.user, public=True, private=False, pinned=True, published=True, recipient=None, date_posted__lte=now, feed=settings.DEFAULT_FEED).exclude(image=None, feed='blog').order_by('-date_posted')
            priv_ids = Post.objects.filter(posted=True, author=profile.user, private=False, public=False, pinned=False, recipient=None, published=True, date_posted__lte=now, feed=settings.DEFAULT_FEED).exclude(image=None, feed='blog').order_by('-date_posted').values_list('id', flat=True)[:settings.PAID_POSTS_SELECTION]
            priv = Post.objects.filter(id__in=list(priv_ids)).order_by('?')[:settings.PAID_POSTS]
            rec = Post.objects.filter(posted=True, author=profile.user, private=False, public=False, pinned=False, recipient=request.user if request.user.is_authenticated else None, published=True, date_posted__lte=now, feed=settings.DEFAULT_FEED).exclude(image=None, feed='blog').order_by('-date_posted') if request.user.is_authenticated else []
            posts = unique(list(chain(pins, priv, rec, ids)))[:settings.FREE_POSTS]
            post = posts[index%len(posts)]
            if post.public:
                url = post.get_face_blur_thumb_url()
            else:
                url = post.get_blur_thumb_url()
    else:
        posts = []
        if request.GET.get('q', None):

            posts = get_posts_for_query(request, request.GET.get('q'))
        post = posts[index%len(posts)]
        if request.user.is_authenticated and (post.author in request.user.profile.subscriptions.all() or (request.user == post.author or (post.recipient and post.recipient == request.user))):
            url = post.get_image_url() if not square else post.get_image_thumb_url()
        elif post.public:
            url = post.get_face_blur_url() if not square else post.get_face_blur_thumb_url()
        elif not post.public:
            url = post.get_blur_url() if not square else post.get_blur_thumb_url()
            #if not url or url == '/media/static/default.png': url = post.get_face_blur_url() if not square else post.get_face_blur_thumb_url()
    full_url = url #request.path + get_qs(request.GET)
    if square:
        addstyle = ''
        from feed.templatetags.app_filters import highlight_query
        if not post.public and not (post.recipient == request.user or (request.user.is_authenticated and post.author in request.user.profile.subscriptions.all())) and not (request.user == post.author and request.GET.get('show', False)): addstyle = 'filter: blur(8px); '
        if request.user.is_authenticated and (post.author in request.user.profile.subscriptions.all() or (request.user == post.author or (post.recipient and post.recipient == request.user))):
            full_url = post.get_image_url()
        result = '<img id="image{}" style="{}position: relative; left: 2%; margin-left: 1%; margin-right: 1%; margin-top: 2%;" data-value="'.format(index, addstyle) + '@{} - {}'.format(post.author.profile.name, highlight_query(request.GET.get('q', None), translate(request, post.content)) if request.GET.get('q') else translate(request, post.content)) + '" data-title="' + post.get_absolute_url() + '" data-fullurl="' + full_url + '" src="' + url + '" class="frame rounded hide"></img>' # width="30%"
    else:
        result = url
    resp = HttpResponse(result)
    if request.user.is_authenticated: patch_cache_control(resp, private=True)
    else: patch_cache_control(resp, public=True)
    return resp

#@login_required
#@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@cache_page(60*60*24*7)
def profile_grid(request, username):
    from misc.views import get_posts_for_query
    from django.core.paginator import Paginator
    from itertools import chain
    from django.utils import timezone
    from security.middleware import get_qs
    from misc.views import get_posts_for_query
    from itertools import chain
    import datetime
    from users.models import Profile
    import pytz
    from feed.models import Post
    from django.http import HttpResponse
    from django.shortcuts import render, get_object_or_404
    from lotteh.pricing import get_pricing_options
    now = timezone.now()
    likes = request.GET.get('likes')
    profile = get_object_or_404(Profile, name=username, vendor=True)
    posts = None
    pins = None
    following = False
    if likes and request.user.is_authenticated:
        posts = request.user.profile.likes.filter(posted=True, author=profile.user, private=False, published=True, public=False, feed=settings.DEFAULT_FEED).union(request.user.profile.likes.filter(author=profile.user, private=True, recipient=request.user, published=True, feed=settings.DEFAULT_FEED)).exclude(image=None, feed='blog').order_by('-date_posted')
    elif request.user.is_authenticated and (profile.user in request.user.profile.subscriptions.all() or (request.user == profile.user and request.GET.get('show', False))):
        following = True
        ids = list(Post.objects.filter(posted=True, author=profile.user, private=False, published=True, feed=settings.DEFAULT_FEED).exclude(image=None, feed='blog').order_by('-date_posted'))
        pins = list(Post.objects.filter(posted=True, author=profile.user, private=False, public=True, pinned=True, published=True, feed=settings.DEFAULT_FEED).exclude(image=None, feed='blog').order_by('-date_posted'))
        rec = list(Post.objects.filter(posted=True, author=profile.user, private=False, public=False, pinned=False, recipient=request.user if request.user.is_authenticated else None, published=True, date_posted__lte=now, feed=settings.DEFAULT_FEED).exclude(image=None, feed='blog').order_by('-date_posted') if request.user.is_authenticated else [])
        from barcode.tests import document_scanned
        if request.user.is_authenticated and document_scanned(request.user):
            ids = ids.union(Post.objects.filter(posted=True, author=profile.user, secure=True, private=True, public=False, pinned=False, published=True, date_posted__lte=now, feed=settings.DEFAULT_FEED).exclude(image=None, feed='blog').order_by('-date_posted') if request.user.is_authenticated else []).order_by('-date_posted')
        posts = unique(list(chain(pins, rec, ids)))
    else:
        ids = list(Post.objects.filter(posted=True, author=profile.user, public=True, private=False, published=True, feed=settings.DEFAULT_FEED).exclude(image=None, feed='blog').order_by('-date_posted'))
        pins = list(Post.objects.filter(posted=True, author=profile.user, public=True, private=False, pinned=True, published=True, feed=settings.DEFAULT_FEED).exclude(image=None, feed='blog').order_by('-date_posted'))
        priv_ids = Post.objects.filter(posted=True, author=profile.user, private=False, public=False, pinned=False, recipient=None, published=True, date_posted__lte=now, feed=settings.DEFAULT_FEED).exclude(image=None, feed='blog').order_by('-date_posted').values_list('id', flat=True)[:settings.PAID_POSTS_SELECTION]
        priv = Post.objects.filter(id__in=list(priv_ids)).order_by('?')[:settings.PAID_POSTS]
        rec = list(Post.objects.filter(posted=True, author=profile.user, private=False, public=False, pinned=False, recipient=request.user if request.user.is_authenticated else None, published=True, date_posted__lte=now, feed=settings.DEFAULT_FEED).exclude(image=None, feed='blog').order_by('-date_posted') if request.user.is_authenticated else [])
        posts = unique(list(chain(pins, priv, rec, ids)))[:settings.FREE_POSTS]
    from lotteh.pricing import get_pricing_options
    choices = []
    for option in get_pricing_options(settings.PHOTO_CHOICES):
        choices = choices + [['${}'.format(sub_fee(option))]]
    resp = render(request, 'feed/profile_grid.html', {
        'title': '@' + profile.name + '\'s Grid',
        'count': len(posts),
        'profile': profile,
        'following': following,
        'preload': True,
        'load_timeout': 10000,
        'full': True,
        'hiderrm': True if request.GET.get('handtrack', False) else False,
        'tip_options': choices
    })
    if request.user.is_authenticated: patch_cache_control(resp, private=True)
    else: patch_cache_control(resp, public=True)
    return resp

#@login_required
#@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@csrf_exempt
def secure_photo(request, filename):
    import os
    try:
        image_data = open(os.path.join(settings.BASE_DIR, 'media/secure/media/', filename), "rb").read()
    except:
        from django.http import Http404
        raise Http404
    ext = filename.split('.')[1]
    u = filename.split('.')[0].split('-')[-1]
#    if u == 's':
#        u = int(filename.split('.')[0].split('-')[-2])
#        if not request.user.is_authenticated or not u == request.user.id:
#            raise PermissionDenied()
    from django.http import HttpResponse
    return HttpResponse(image_data, content_type="image/{}".format(ext))

@csrf_exempt
@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def rotate(request, pk, direction):
    from django.core.exceptions import PermissionDenied
    from feed.models import Post
    from django.shortcuts import redirect
    post = Post.objects.get(id=pk)
    if not request.user == post.author:
        raise PermissionDenied()
    if request.method == 'POST':
        print('post')
        if direction == 'left':
            post.rotate_left()
            post.save()
        if direction == 'flip':
            post.rotate_flip()
            post.save()
        if direction == 'right':
            post.rotate_right()
            post.save()
        from django.contrib import messages
        messages.success(request, 'Rotated post ' + direction)
    return redirect(post.get_absolute_url())

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def subscriptions(request):
    from users.models import Profile
    from django.contrib import messages
    from django.core.paginator import Paginator
    profiles = Profile.objects.filter(vendor=True, user__is_superuser=False, user__in=request.user.profile.subscriptions.all()).order_by('-last_seen')
    page = 1
    if(request.GET.get('page', '') != ''):
        page = int(request.GET.get('page', ''))
    p = Paginator(profiles, 10)
    if page > p.num_pages or page < 1:
        messages.warning(request, "The page you requested, " + str(page) + ", does not exist. You have been redirected to the first page.")
        page = 1
    from django.shortcuts import render
    return render(request, 'feed/subscriptions.html', {
        'title': 'Active Subscriptions',
        'profiles': p.page(page),
        'count': p.count,
        'page_obj': p.get_page(page),
    })


@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def unfollow(request, username):
    from django.shortcuts import render, get_object_or_404
    from django.contrib.auth.models import User
    user = get_object_or_404(User, profile__name=username)
    if request.method == 'POST' and user in request.user.profile.subscriptions.all():
        p = request.user.profile
        p.subscriptions.remove(user)
        p.save()
        for sub in Subscription.objects.filter(user=request.user, model=user, active=True):
            sub.active = False
            sub.save()
        from django.shortcuts import redirect
        from django.urls import reverse
        return redirect(reverse('feed:profile', kwargs={'username': username}))
    return render(request, 'feed/confirm_cancel.html', {'cancel_user': user})

#@login_required
#@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@cache_page(60*60*24*365)
def follow(request, username):
    from django.shortcuts import get_object_or_404, render, redirect
    from django.urls import reverse
    from django.contrib.auth.models import User
    from contact.forms import ContactForm
    user = get_object_or_404(User, profile__name=username)
    if request.user.is_authenticated and user in request.user.profile.subscriptions.all() and user.profile.vendor:
        return redirect(reverse('feed:profile', kwargs={'username': username}))
    return render(request, 'feed/follow.html', {
        'title': 'Perks of following {}'.format(user.profile.name),
        'p_user': user,
        'contact_form': ContactForm(),
    })
#    return redirect(reverse('feed:profile', kwargs={'username': username}))

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def home(request):
    from django.core.paginator import Paginator
    from feed.models import Post
    from django.contrib import messages
    page = 1
    if(request.GET.get('page', '') != ''):
        page = int(request.GET.get('page', ''))
    posts = Post.objects.filter(posted=True, author__profile__identity_verified=True, author__profile__vendor=True, private=False, author__in=request.user.profile.subscriptions.all(), published=True).order_by('-date_posted')
    p = Paginator(posts, 10)
    if page > p.num_pages or page < 1:
        messages.warning(request, "The page you requested, " + str(page) + ", does not exist. You have been redirected to the first page.")
        page = 1
    from django.shortcuts import render
    return render(request, 'feed/home.html', {
        'title': 'Your Feed',
        'posts': p.page(page),
        'count': p.count,
        'page_obj': p.get_page(page),
    })

#@login_required
#@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@cache_page(60*60*24*365)
def profiles(request):
    from django.core.paginator import Paginator
    from django.contrib import messages
    from users.models import Profile
    from django.shortcuts import render
    profiles = Profile.objects.filter(vendor=True, user__is_superuser=False, user__vendor_profile__hide_profile=False).order_by('-last_seen')
    page = 1
    if(request.GET.get('page', '') != ''):
        page = int(request.GET.get('page', ''))
    p = Paginator(profiles, 10)
    if page > p.num_pages or page < 1:
        messages.warning(request, "The page you requested, " + str(page) + ", does not exist. You have been redirected to the first page.")
        page = 1
    return render(request, 'feed/profiles.html', {
        'title': 'See Who\'s Active',
        'profiles': p.page(page),
        'count': p.count,
        'page_obj': p.get_page(page),
    })

#@login_required
#@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@csrf_exempt
@cache_page(60*60*24*7)
@vary_on_cookie
def profile(request, username):
    from django.conf import settings
    from django.utils import timezone
    from django.core.paginator import Paginator
    from django.contrib import messages
    from users.models import Profile
    from django.shortcuts import render, redirect, get_object_or_404
    from django.urls import reverse
    from itertools import chain
    import datetime, pytz
    from feed.models import Post
    from security.middleware import get_qs
    now = None
    try:
        now = datetime.datetime.fromtimestamp(int(request.GET.get('time')) / 1000, tz=pytz.UTC)
    except:
        now = timezone.now()
    if not request.GET.get('feed', False):
        return redirect(request.path + (get_qs(request.GET) if get_qs(request.GET) else '?') + '&feed=private')
    blog_feed = request.GET.get('feed')
    likes = request.GET.get('likes')
    pages = request.GET.get('pages')
    scroll_page = request.GET.get('scroll_page')
    profile = get_object_or_404(Profile, name=username, vendor=True)
    page = 1
    if(request.GET.get('page', '') != ''):
        page = int(request.GET.get('page', ''))
    ids = None
    following = False
    pins = None
    posts = None
    if likes and request.user.is_authenticated:
        posts = request.user.profile.likes.filter(posted=True, author=profile.user, private=False, published=True, date_posted__lte=now).union(request.user.profile.likes.filter(author=profile.user, private=True, recipient=request.user, published=True)).order_by('-date_posted')
    elif request.user.is_authenticated and profile.user in request.user.profile.subscriptions.all() or (request.user == profile.user and request.GET.get('show', False)):
        following = True
        ids = Post.objects.filter(posted=True, author=profile.user, private=False, published=True, date_posted__lte=now).union(Post.objects.filter(author=profile.user, private=True, recipient=request.user, published=True, date_posted__lte=now, feed=blog_feed)).order_by('-date_posted')
        pins = Post.objects.filter(posted=True, author=profile.user, public=True, private=False, pinned=True, published=True, date_posted__lte=now, feed=blog_feed).order_by('-date_posted')
        rec = Post.objects.filter(posted=True, author=profile.user, private=False, public=False, pinned=False, recipient=request.user if request.user.is_authenticated else None, published=True, date_posted__lte=now, feed=blog_feed).order_by('-date_posted') if request.user.is_authenticated else []
        from barcode.tests import document_scanned
        if request.user.is_authenticated and document_scanned(request.user):
            ids = ids.union(Post.objects.filter(posted=True, author=profile.user, secure=True, private=True, public=False, pinned=False, published=True, date_posted__lte=now, feed=settings.DEFAULT_FEED).exclude(image=None, feed='blog').order_by('-date_posted') if request.user.is_authenticated else []).order_by('-date_posted')
        posts = unique(list(chain(pins, rec, ids)))
    else:
        ids = Post.objects.filter(posted=True, author=profile.user, public=True, private=False, published=True, date_posted__lte=now, feed=blog_feed).order_by('-date_posted')
        pins = Post.objects.filter(posted=True, author=profile.user, public=True, private=False, pinned=True, published=True, date_posted__lte=now, feed=blog_feed).order_by('-date_posted')
        priv_ids = Post.objects.filter(posted=True, author=profile.user, private=False, public=False, pinned=False, recipient=None, published=True, date_posted__lte=now, feed=blog_feed).order_by('-date_posted').values_list('id', flat=True)[:settings.PAID_POSTS_SELECTION]
        priv = Post.objects.filter(id__in=list(priv_ids)).order_by('?')[:settings.PAID_POSTS]
        rec = Post.objects.filter(posted=True, author=profile.user, private=False, public=False, pinned=False, recipient=request.user if request.user.is_authenticated else None, published=True, date_posted__lte=now, feed=blog_feed).order_by('-date_posted') if request.user.is_authenticated else []
        posts = unique(list(chain(pins, rec, priv, ids)))[:settings.FREE_POSTS]
    if not request.user.is_authenticated or not (profile.user in request.user.profile.subscriptions.all() or request.user == profile.user):
        posts = posts[:settings.FREE_POSTS]
    p = Paginator(posts, 10)
    if page > p.num_pages or page < 1:
        messages.warning(request, "The page you requested, " + str(page) + ", does not exist. You have been redirected to the first page.")
        page = 1
    from lotteh.pricing import get_pricing_options
    choices = []
    for option in get_pricing_options(settings.PHOTO_CHOICES):
        choices = choices + [['${}'.format(sub_fee(option))]]
    resp = render(request, 'feed/profile.html' if pages else 'feed/scroll_page.html' if scroll_page else 'feed/scroll.html', {
        'title': '@' + profile.name + '\'s Profile',
        'posts': p.page(page),
        'count': len(posts),
        'page_obj': p.get_page(page),
        'profile': profile,
        'following': following,
        'preload': True,
        'tip_options': choices,
        'num_pages': p.num_pages,
        'page': page,
        'firstPage': page == p.num_pages,
        'webpush-override': True,
        'full': True,
        'hidenavbar': True if scroll_page else False,
        'load_timeout': 0 if scroll_page else 5000,
    })
    if request.user.is_authenticated: patch_cache_control(resp, private=True)
    else: patch_cache_control(resp, public=True)
    return resp

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def all(request):
    from django.core.paginator import Paginator
    from django.contrib import messages
    from feed.models import Post
    from django.shortcuts import render
    if not request.user.profile.identity_verified:
        messages.warning(request, 'You need to verify your identity before you may see this page.')
        return redirect(reverse("verify:verify"))
    page = 1
    if(request.GET.get('page', None) != None):
        page = int(request.GET.get('page', ''))
    posts = Post.objects.filter(posted=True, author__profile__vendor=True, public=True, private=False).order_by('-date_posted')
    p = Paginator(posts, 10)
    if page > p.num_pages or page < 1:
        messages.warning(request, "The page you requested, " + str(page) + ", does not exist. You have been redirected to the first page.")
        page = 1
    return render(request, 'feed/all.html', {
        'title': 'See All Posts',
        'posts': p.page(page),
        'count': p.count,
        'page_obj': p.get_page(page),
    })

#@login_required
#@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@cache_page(60*60*24*365)
def post_detail(request, uuid):
    from django.core.paginator import Paginator
    from django.contrib import messages
    from feed.models import Post
    from django.shortcuts import render, get_object_or_404
    from django.core.exceptions import PermissionDenied
    post = get_object_or_404(Post, friendly_name=uuid)
    if (((not request.user.is_authenticated or not hasattr(request.user, 'profile') or not post.author in request.user.profile.subscriptions.all()) and not post.public) and post.author != request.user and not post.recipient == request.user) or post.secure and not (request.user.is_authenticated and document_scanned(request.user)):
        raise PermissionDenied()
    title = 'No text in this post. - View Post'
    pagetitle = ''
    description = 'x'
    oc = post.content
    from feed.templatetags.app_filters import clean_html
    post.content = clean_html(post.content)
    if len(post.content.splitlines()) > 0:
        pagetitle = post.content.splitlines()[0][0:70]
        if len(post.content.splitlines()[0]) > 70:
            pagetitle = post.content.splitlines()[0][0:67].rsplit(' ', 1)[0] + '...'
        title = post.content.splitlines()[0][0:38]
        if len(post.content.splitlines()[0]) > 38:
            title = post.content.splitlines()[0][0:38].rsplit(' ', 1)[0] + '...'
        title = '\"' + title + '\" - View Post'
    if len(post.content.splitlines()) > 1:
        description = post.content.splitlines()[1][0:155]
        if len(description) == 0 and len(post.content.splitlines()) > 2:
            description = post.content.splitlines()[2][0:155]
        if len(description) > 152:
            description = description.rsplit(' ', 1)[0] + '...'
    if description == 'x':
        description = pagetitle
    if description == '':
        description = 'No description for this post.' + basedescription
    post.content = oc
    from django.shortcuts import render
    resp = render(request, 'feed/post_detail.html', {'title': title, 'pagetitle': pagetitle, 'post': post})
    if request.user.is_authenticated: patch_cache_control(resp, private=True)
    else: patch_cache_control(resp, public=True)
    return resp

@never_cache
@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
@csrf_exempt
def new_post_confirm(request, id):
    from django.utils import timezone
    import datetime
    from feed.models import Post
    from django.http import HttpResponse
    return HttpResponse('y' if Post.objects.filter(confirmation_id=id, date_uploaded__gte=timezone.now() - datetime.timedelta(minutes=5)).count() > 0 else 'n')


@never_cache
@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def new_post(request):
    from django.contrib import messages
    from django.conf import settings
    import datetime, pytz, os
    from .models import get_file_path, get_image_path
    from django.utils import timezone
    from feed.models import Post
    from .forms import PostForm, ScheduledPostForm
    from django.contrib.auth.models import User
    from django.http import HttpResponse
    from security.security import fraud_detect
    arg = request.GET.get('text','')
    text = ''
    if not arg == '':
        text = arg
    unpublished_post = None
    if not text:
        unpublished_post = Post.objects.filter(posted=False, author=request.user).order_by('-date_posted').last()
    if request.method == 'POST' and not fraud_detect(request, True):
        form = PostForm(request.POST, request.FILES, instance=unpublished_post) if not request.GET.get('schedule') else ScheduledPostForm(request.POST, request.FILES, instance=unpublished_post)
        if form.is_valid():
            form.instance.author = request.user
            if not request.GET.get('schedule'): to_post = timezone.now()
            else:
                try:
                    to_post = datetime.datetime.combine(datetime.datetime.strptime(form.data.get('date'), '%Y-%m-%d').date(), datetime.datetime.strptime(form.data.get('time'), '%H:%M:%S.%f').time())
                except:
                    try:
                        to_post = datetime.datetime.combine(datetime.datetime.strptime(form.data.get('date'), '%Y-%m-%d').date(), datetime.datetime.strptime(form.data.get('time'), '%H:%M:%S').time())
                    except:
                        to_post = datetime.datetime.combine(datetime.datetime.strptime(form.data.get('date'), '%Y-%m-%d').date(), datetime.datetime.strptime(form.data.get('time'), '%H:%M').time())
            if to_post < timezone.now(): to_post = timezone.now()
            form.instance.date_posted = to_post - datetime.timedelta(milliseconds=len(request.FILES.getlist('image')) + 2)
            if form.instance.private and form.cleaned_data.get('recipient') != '0' and form.cleaned_data.get('recipient') != '':
                form.instance.recipient = User.objects.get(id=int(form.cleaned_data.get('recipient')))
#            form.instance.published = True
            if request.GET.get('save', False):
                post = form.save()
                post.upload()
                return HttpResponse(200)
            form.instance.posted = True
            files = request.FILES.getlist('image')
            if len(files) > 0:
                f = files[0]
                path = os.path.join(settings.MEDIA_ROOT, get_image_path(form.instance, f.name))
                with open(path, 'wb+') as file:
                    for chunk in f.chunks():
                        file.write(chunk)
                    form.instance.image = path
            files = request.FILES.getlist('file')
            if len(files) > 0:
                f = files[0]
                path = os.path.join(settings.MEDIA_ROOT, get_file_path(form.instance, f.name))
                with open(path, 'wb+') as file:
                    for chunk in f.chunks():
                        file.write(chunk)
                    form.instance.file = path
            post = form.save()
            post.upload()
#            Post.objects.create(public=True, private=False, published=False, posted=False, content='', author=request.user)
            first = True
            if files:
                for index, f in enumerate(files):
                    if not first:
                        post = Post.objects.create(author=request.user, date_posted=to_post - datetime.timedelta(milliseconds=index))
                        path = os.path.join(settings.MEDIA_ROOT, get_image_path(post, f.name))
                        with open(path, 'wb+') as file:
                            for chunk in f.chunks():
                                file.write(chunk)
                        post.image = path
                        post.published = True
                        post.public = form.instance.public
                        post.private = form.instance.private
                        post.save()
                        post.upload()
                    first = False
            first = True
            files = request.FILES.getlist('file')
            if files:
                for index, f in enumerate(files):
                    if not first:
                        post = Post.objects.create(author=request.user, date_posted=to_post - datetime.timedelta(milliseconds=index))
                        path = os.path.join(settings.MEDIA_ROOT, get_file_path(post, f.name))
                        with open(path, 'wb+') as file:
                            for chunk in f.chunks():
                                file.write(chunk)
                        post.file = path
                        post.published = True
                        post.public = form.instance.public
                        post.private = form.instance.private
                        post.save()
                        post.upload()
                    first = False
#            from lotteh.celery import remove_duplicates
            from .duplicates import remove_post_duplicates
            remove_post_duplicates() #.apply_async([post.id], countdown=60)
            messages.success(request, f'Your content has been posted.')
            return HttpResponse(200)
    else:
        f = request.GET.get('feed', None)
        if not f: f = 'private'
        arg = request.GET.get('text','')
        text = ''
        if not arg == '':
            text = arg
            form = PostForm(initial={'feed': f, 'content': text}) if not request.GET.get('schedule') else ScheduledPostForm(initial={'feed': f, 'content': text, 'time': datetime.datetime.now()})
        else:
            form = PostForm(instance=unpublished_post) if not request.GET.get('schedule') else ScheduledPostForm(instance=unpublished_post)
    from django.shortcuts import render
    global use_bs4
    return render(request, 'feed/new_post.html', {'title': 'New Post', 'form': form, 'full': True, 'upload_interval': settings.UPLOAD_INTERVAL, 'bs4': use_bs4, 'headjs': True})

from .forms import PostForm, ScheduledPostForm, UpdatePostForm
from .models import Post

@method_decorator(never_cache, name='dispatch')
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = UpdatePostForm
    object = None

    def get(self, request, pk):
        from django.shortcuts import render
        from django.http import HttpResponseRedirect
        self.object = self.get_object()
        if '***' in self.get_object().content and not request.GET.get('raw', None): return HttpResponseRedirect(request.path + '?raw=t')
        return render(request, self.template_name, self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_initial(self):
        import pytz
        return {'time': self.get_object().date_posted.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%H:%M:00'), 'date': self.get_object().date_posted.astimezone(pytz.timezone(settings.TIME_ZONE)).date} #.strftime('%m-%d-%Y')

    def form_valid(self, form):
        from django.contrib import messages
        self.object = self.get_object()
        form.instance.author = self.request.user
        messages.success(self.request, f'Your post has been updated.')
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if identity_verified(self.request.user) and is_vendor(self.request.user) and self.request.user == post.author:
            return True
        return False

from django.urls import reverse_lazy

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('go:go')

    def get_success_url(self):
        from django.urls import reverse
        return reverse('go:go')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def test_func(self):
        post = self.get_object()
        if identity_verified(self.request.user) and is_vendor(self.request.user) and self.request.user == post.author or (self.request.user.is_superuser and not post.author.is_superuser) and not fraud_detect(request, True):
            return True
        return False

class RangeFileWrapper(object):
    def __init__(self, filelike, blksize=8192, offset=0, length=None):
        import os
        self.filelike = filelike
        self.filelike.seek(offset, os.SEEK_SET)
        self.remaining = length
        self.blksize = blksize

    def close(self):
        if hasattr(self.filelike, 'close'):
            self.filelike.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self.remaining is None:
            # If remaining is None, we are reading the entire file.
            data = self.filelike.read(self.blksize)
            if data:
                return data
            raise StopIteration()
        else:
            if self.remaining <= 0:
                raise StopIteration()
            data = self.filelike.read(min(self.remaining, self.blksize))
            if not data:
                raise StopIteration()
            self.remaining -= len(data)
            return data


#@login_required
#@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def secure_video(request, filename):
    u = int(filename.split('.')[0].split('-')[-1])
    from django.core.exceptions import PermissionDenied
    if request.user.is_authenticated and u != request.user.id:
        raise PermissionDenied()
    import os, re, mimetypes
    from wsgiref.util import FileWrapper
    from django.conf import settings
    from django.http.response import StreamingHttpResponse
    range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)
    path = os.path.join(settings.BASE_DIR, 'media/secure/video/', filename)
    range_header = request.META.get('HTTP_RANGE', '').strip()
    range_match = range_re.match(range_header)
    size = os.path.getsize(path)
    content_type, encoding = mimetypes.guess_type(path)
    content_type = content_type or 'application/octet-stream'
    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        last_byte = int(last_byte) if last_byte else size - 1
        if last_byte >= size:
            last_byte = size - 1
        length = last_byte - first_byte + 1
        resp = StreamingHttpResponse(RangeFileWrapper(open(path, 'rb'), offset=first_byte, length=length), status=206, content_type=content_type)
        resp['Content-Length'] = str(length)
        resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
    else:
        resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')), content_type=content_type)
        resp['Content-Length'] = str(size)
    resp['Accept-Ranges'] = 'bytes'
    return resp
