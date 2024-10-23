from django.contrib.auth.decorators import user_passes_test
from vendors.tests import is_vendor
from feed.tests import identity_verified
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import patch_cache_control
from django.views.decorators.vary import vary_on_cookie
from django.views.decorators.cache import cache_page

@cache_page(60*60*24)
@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def go(request):
    from django.shortcuts import render
    from django.shortcuts import redirect
    from django.urls import reverse
    from django.utils import timezone
    from django.contrib.sessions.models import Session
    from security.views import all_unexpired_sessions_for_user
    from django.contrib.auth.models import User
    from feed.models import Post
    from django.conf import settings
    from recovery.tensordock import get_balance
    from barcode.models import DocumentScan
    import datetime
#    if not request.user.profile.vendor:
#        return redirect(reverse('landing:landing'))
    sc = 0
#    for user in User.objects.all():
#        sc = sc + len(all_unexpired_sessions_for_user(user))
#    pins = Post.objects.filter(author=request.user, public=True, private=False, pinned=True).order_by('-date_posted')
#    users = User.objects.filter(is_active=True).count()
#    verified_users = User.objects.filter(is_active=True)
#    verified_user_count = 0
#    for user in verified_users:
#        verified_user_count = verified_user_count + (1 if user.verifications.count() > 0 else 0)
#    active_today = User.objects.filter(is_active=True, profile__last_seen__gte=timezone.now()-datetime.timedelta(days=1)).count()
#    active_this_week = User.objects.filter(is_active=True, profile__last_seen__gte=timezone.now()-datetime.timedelta(days=7)).count()
#    active_this_month = User.objects.filter(is_active=True, profile__last_seen__gte=timezone.now()-datetime.timedelta(days=30)).count()
#    active_this_year = User.objects.filter(is_active=True, profile__last_seen__gte=timezone.now()-datetime.timedelta(days=365)).count()
    id = DocumentScan.objects.filter(user=request.user, side=True).last().document_isolated.url if DocumentScan.objects.filter(user=request.user, side=True).last() and DocumentScan.objects.filter(user=request.user, side=True).last().document_isolated else ''
    smp = None #Post.objects.filter(id=settings.STATUS_SAMPLE).first()
    post = Post.objects.filter(id=settings.SPLASH).first()
#    ad_post = Post.objects.filter(public=False, private=True, feed="ad", author__id=settings.MY_ID).last()
    ad_post = None
    status_messages = None #smp.content.split('\n') if smp else []
    r = render(request, 'go/go.html', {'title': 'Go', 'session_count': sc, 'status_messages': status_messages, 'smp_id': smp.id if smp else 1, 'splash_id': post.id if post else 1, 'digital_id': id, 'ad_post': ad_post.id if ad_post else None})
    patch_cache_control(r, private=True)
    return r
# 'user_count': users, 'verified_user_count': verified_user_count, 'active_today': active_today, 'active_this_week': active_this_week, 'active_this_month': active_this_month, 'active_this_year': active_this_year, 
