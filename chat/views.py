from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import user_passes_test
from feed.tests import identity_verified
from vendors.tests import is_vendor
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import (
    DeleteView
)

from .models import Message


class ChatDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Message
    success_url = '/chat/'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def test_func(self):
        post = self.get_object()
        if identity_verified(self.request.user) and is_vendor(self.request.user) or self.request.user == post.sender or (self.request.user.is_superuser and not post.author.is_superuser) and not fraud_detect(request, True):
            return True
        return False

def video_redirect(request, s):
    from django.shortcuts import redirect
    from django.urls import reverse
    return redirect(reverse('chat:video'))

def mirror(request):
    from django.shortcuts import render, redirect, get_object_or_404
    return render(request, 'chat/mirror.html', {'hidenavbar': True, 'full': True})

@never_cache
def video(request): #, username):
    from django.shortcuts import render, redirect, get_object_or_404
#    from users.models import Profile
#    profile = get_object_or_404(Profile, name=username)
    from users.username_generator import generate_username
    profile = None
    return render(request, 'chat/video.html', {'title': 'Video Chat', 'profile': profile, 'thename': generate_username(), 'full': True})

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def chat_self(request):
    from django.shortcuts import render, redirect, get_object_or_404
    from django.urls import reverse
    from django.contrib.auth.models import User
    from users.models import Profile
    from django.contrib import messages
    from .forms import MessageForm
    import datetime
    from django.core.paginator import Paginator
    from .models import Message
    from django.utils.decorators import method_decorator
    from django.http import HttpResponse
    from security.security import fraud_detect
    return redirect(reverse('chat:chat', kwargs={'username': request.user.profile.name}))

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def chat(request, username):
    from django.shortcuts import render, redirect, get_object_or_404
    from django.urls import reverse
    from django.contrib.auth.models import User
    from users.models import Profile
    from django.contrib import messages
    from .forms import MessageForm
    import datetime
    from django.core.paginator import Paginator
    from .models import Message
    from django.utils.decorators import method_decorator
    from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
    from django.core.exceptions import PermissionDenied
    from django.http import HttpResponse
    from security.security import fraud_detect
    from django.views.generic import (
        ListView,
        DetailView,
        CreateView,
        UpdateView,
        DeleteView
    )
    profile = get_object_or_404(Profile, name=username, identity_verified=True)
    recipient = get_object_or_404(User, profile__name=username)
    page = 1
    if(request.GET.get('page', '') != ''):
        page = int(request.GET.get('page', ''))
    msgs = None
    if recipient == request.user:
        msgs = Message.objects.filter(sender__profile__identity_verified=True, recipient__profile__identity_verified=True, recipient=recipient).order_by('-sent_at')
    else:
        msgs = Message.objects.filter(sender__profile__identity_verified=True, recipient__profile__identity_verified=True, sender=recipient).union(Message.objects.filter(sender__profile__identity_verified=True, recipient__profile__identity_verified=True, sender=request.user)).order_by('-sent_at')
    p = Paginator(msgs, 10)
    if page > p.num_pages or page < 1:
        messages.warning(request, "The page you requested, " + str(page) + ", does not exist. You have been redirected to the first page.")
        page = 1
    content = ''
    hidenav = None
    if request.GET.get('hidenavbar','') != '':
        hidenav = True
    if request.GET.get('text','') != '':
        content = request.GET.get('text','')
    form = MessageForm(initial={'content': content})
    if request.method == "POST" and not fraud_detect(request, True):
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save()
            message.sender = request.user
            message.recipient = profile.user
            message.save()
            from django.conf import settings
            payload = {'head': 'New message from {}'.format(message.sender.username), 'body': message.content, 'icon': '{}{}'.format(settings.BASE_URL, settings.ICON_URL)}
            from pwa_webpush import send_user_notification
            try:
                send_user_notification(recipient, payload=payload)
            except: pass
            messages.success(request, f'Your message has been sent.')
            return redirect('chat:chat', username=username)
    return render(request, 'chat/chat.html', {
        'title': 'Chat Messages',
        'msgs': p.page(page),
        'count': p.count,
        'page_obj': p.get_page(page),
        'form': form,
        'profile': profile,
        'hidenavbar': hidenav,
    })

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def has_message(request, username):
    from django.shortcuts import render, redirect, get_object_or_404
    from django.urls import reverse
    from django.contrib.auth.models import User
    from users.models import Profile
    from django.contrib import messages
    from .forms import MessageForm
    import datetime
    from django.core.paginator import Paginator
    from .models import Message
    from django.utils.decorators import method_decorator
    from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
    from django.core.exceptions import PermissionDenied
    from django.http import HttpResponse
    from security.security import fraud_detect
    from django.views.generic import (
        ListView,
        DetailView,
        CreateView,
        UpdateView,
        DeleteView
    )
    page = 1
    recipient = get_object_or_404(User, profile__name=username)
    msgs = None
    if recipient == request.user:
        msgs = Message.objects.filter(sender__profile__identity_verified=True, recipient__profile__identity_verified=True, recipient=recipient).order_by('-sent_at')
    else:
        msgs = Message.objects.filter(sender__profile__identity_verified=True, recipient__profile__identity_verified=True, sender=recipient).union(Message.objects.filter(sender__profile__identity_verified=True, recipient__profile__identity_verified=True, sender=request.user)).order_by('-sent_at')
    p = Paginator(msgs, 10)
    for m in p.get_page(page):
        if (m.sender == request.user and m.senderseen == False) or m.seen == False:
            return HttpResponse('1')
    return HttpResponse('0')


@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def raw(request, username):
    from django.shortcuts import render, redirect, get_object_or_404
    from django.urls import reverse
    from django.contrib.auth.models import User
    from users.models import Profile
    from django.contrib import messages
    from .forms import MessageForm
    import datetime
    from django.core.paginator import Paginator
    from .models import Message
    from django.utils.decorators import method_decorator
    from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
    from django.core.exceptions import PermissionDenied
    from django.http import HttpResponse
    from security.security import fraud_detect
    from django.views.generic import (
        ListView,
        DetailView,
        CreateView,
        UpdateView,
        DeleteView
    )
    recipient = get_object_or_404(User, profile__name=username)
    page = 1
    if(request.GET.get('page', '') != ''):
        page = int(request.GET.get('page', ''))
    msgs = None
    if recipient == request.user:
        msgs = Message.objects.filter(sender__profile__identity_verified=True, recipient__profile__identity_verified=True, recipient=recipient).order_by('-sent_at')
    else:
        msgs = Message.objects.filter(sender__profile__identity_verified=True, recipient__profile__identity_verified=True, sender=recipient).union(Message.objects.filter(sender__profile__identity_verified=True, recipient__profile__identity_verified=True, sender=request.user)).order_by('-sent_at')
    p = Paginator(msgs, 10)
    if page > p.num_pages or page < 1:
        messages.warning(request, "The page you requested, " + str(page) + ", does not exist. You have been redirected to the first page.")
        page = 1
    for message in p.page(page):
        if message.recipient == request.user:
            message.seen = True
            message.save()
        if message.sender == request.user:
            message.senderseen = True
            message.save()
    context = {
        'messages': p.page(page),
        'count': p.count,
        'page_obj': p.get_page(page),
    }
    return render(request, 'chat/messages_raw.html', context)

