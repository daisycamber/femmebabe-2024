from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from vendors.tests import is_vendor
from feed.tests import identity_verified
from vendors.tests import is_vendor
from django.views.decorators.csrf import csrf_exempt

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def add_option(request):
    from .forms import ChoiceCreateForm
    from django.contrib import messages
    hidenavbar = False
    if request.GET.get('hidenavbar', False):
        hidenavbar = True
    if request.method == "POST":
        form = ChoiceCreateForm(request.POST)
        form.instance.user = request.user
        form.save()
        messages.success(request, 'The option, {}, has been saved.'.format(form.instance.option))
    return render(request, 'interactive/forms.html', {'form': ChoiceCreateForm(), 'hidenavbar': hidenavbar, 'small': True})


@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def interactive(request, username):
    from django.urls import reverse
    from django.contrib import messages
    from django.contrib.auth.models import User
    model = User.objects.get(profile__name=username)
    if (not model in request.user.profile.subscriptions.all()) and not model == request.user:
        messages.warning(request, 'You need to follow {} before you can see their interactive feed.'.format(username))
        return redirect(reverse('feed:follow', kwargs={'username': username}))
    return render(request, 'interactive/interactive.html', {
        'title': 'Interactive - @' + username,
        'model': model,
        'compressed': True
    })

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def interactive_frame(request, username):
    from live.models import VideoRecording
    from django.core.paginator import Paginator
    from django.contrib import messages
    from django.contrib.auth.models import User
    model = User.objects.get(profile__name=username)
    if (not model in request.user.profile.subscriptions.all()) and not model == request.user:
        messages.warning(request, 'You need to follow {} before you can see their interactive feed.'.format(username))
        return redirect(reverse('feed:follow', kwargs={'username': username}))
    recording = VideoRecording.objects.filter(camera='private', safe=True, public=True, processed=True).order_by('?').first()
    return recording.file_processed.url

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def forms(request, username):
    from django.urls import reverse
    from django.utils import timezone
    from live.models import VideoRecording
    from .forms import ChoicesForm
    from .models import Choices
    from django.contrib import messages
    from django.contrib.auth.models import User
    if not request.user.profile.interactive == request.GET.get('interactive'):
        import urllib.parse
        request.GET._mutable = True
        request.GET.interactive = urllib.parse(request.user.profile.interactive)
        return redirect(request.path + get_qs(request.GET))
    model = User.objects.get(profile__name=username)
    if (not model in request.user.profile.subscriptions.all()) and not model == request.user:
        messages.warning(request, 'You need to follow {} before you can see their interactive feed.'.format(username))
        return redirect(reverse('feed:follow', kwargs={'username': username}))
    hidenavbar = False
    if request.GET.get('hidenavbar', False):
        hidenavbar = True
    if request.method == "POST":
        form = ChoicesForm(request.POST)
        choices = Choices.objects.filter(label=form.data['choice'])
        c = None
        if choices.count() > 0:
            c = choices.first().interactive
        else:
            c = 'What would you like me to do?'
        request.user.profile.interactive = c
        request.user.profile.save()
    return render(request, 'interactive/forms.html', {'form': ChoicesForm(), 'hidenavbar': hidenavbar})

@csrf_exempt
@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def recording(request, username):
    from django.urls import reverse
    from live.models import VideoRecording
    from django.contrib import messages
    from django.contrib.auth.models import User
    from django.urls import reverse
    from live.models import VideoRecording
    from django.contrib import messages
    from django.contrib.auth.models import User
    model = User.objects.get(profile__name=username)
    if (not model in request.user.profile.subscriptions.all()) and not model == request.user:
        messages.warning(request, 'You need to follow {} before you can see their interactive feed.'.format(username))
        return redirect(reverse('feed:follow', kwargs={'username': username}))
    recordings = VideoRecording.objects.filter(interactive=request.user.profile.interactive)
    if recordings.count() == 0:
        request.user.profile.interactive = "What would you like me to do?"
        request.user.profile.save()
    recording = recordings.first()
    frame = recording.get_file_url()
    return render(request, 'interactive/frame.html', {'title': 'Recording', 'frame': frame})
