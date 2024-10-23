from django.contrib.auth.decorators import user_passes_test
from vendors.tests import is_vendor
from feed.tests import identity_verified
from django.contrib.auth.decorators import login_required

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def send_guest_notification(request):
    from django.shortcuts import render
    from .forms import NotificationForm
    from django.conf import settings
    from django.contrib import messages
    import traceback
    from feed.models import Post
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data.get('url', None)
            posts = Post.objects.filter(author__id=settings.MY_ID, enhanced=True, private=False, public=True, published=True, recipient=None).exclude(image=None).order_by('-date_posted').values_list('id', flat=True)[:settings.FREE_POSTS]
            post = Post.objects.filter(id__in=posts).order_by('?').first()
            payload = {"head": form.cleaned_data.get('head', 'Visit {}'.format(settings.SITE_NAME)), "body": form.cleaned_data.get('body', 'Enjoy your time with {}'.format(settings.SITE_NAME)), 'icon': post.get_face_blur_thumb_url(), 'url': settings.BASE_URL if not url else url}
            messages.success(request, 'Successful push notification - {}'.format(form.cleaned_data.get('head')))
            from pwa_webpush import send_group_notification
            try:
                send_group_notification(group_name="guests", payload=payload, ttl=1000)
            except: pass
    return render(request, 'notifications/send.html', {'title': 'Send Notification', 'form': NotificationForm()})