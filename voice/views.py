from django.views.decorators.csrf import csrf_exempt
from feed.tests import identity_verified
from django.contrib.auth.decorators import user_passes_test
from vendors.tests import is_vendor
from django.conf import settings
from django.contrib.auth.decorators import login_required

def interactive(key):
    from .models import AudioInteractive
    from django.conf import settings
    return settings.BASE_URL + AudioInteractive.objects.filter(label=key).last().get_secure_url()

account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def call_recordings(request):
    from django.shortcuts import render
    from django.shortcuts import redirect, get_object_or_404
    from django.urls import reverse
    from django.utils import timezone
    from django.contrib.sessions.models import Session
    from live.models import VideoRecording
    from django.core.paginator import Paginator
    from django.views.decorators.csrf import csrf_exempt
    from .forms import AudioInteractiveForm, ChoiceCreateForm
    from django.contrib import messages
    from django.utils import timezone
    import os, pytz
    from .models import Call
    from django.http import HttpResponse
    from django.contrib.auth.models import User
    import threading
    import time
    from users.tfa import send_user_text
    import datetime
    from .models import AudioInteractive
    from twilio.rest import Client
    client = Client(account_sid, auth_token)
    recordings = client.recordings.list(limit=20)
    urls = list()
    for recording in recordings:
        call = None
        try:
            call = Call.objects.get(sid=recording.sid)
        except:
            call = None
        urls.append((call.user.profile.phone_number if call else 'unknown', call.call_time.astimezone(pytz.timezone(settings.TIME_ZONE)) if call else 'unknown', recording.media_url))
    return render(request, 'voice/calls.html', {'title': 'Phone Calls', 'urls': urls})

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def option_add(request):
    from django.shortcuts import render
    from django.contrib.auth.decorators import login_required
    from django.shortcuts import redirect, get_object_or_404
    from django.urls import reverse
    from django.utils import timezone
    from django.contrib.auth.decorators import user_passes_test
    from vendors.tests import is_vendor
    from feed.tests import identity_verified
    from vendors.tests import is_vendor
    from django.contrib.sessions.models import Session
    from live.models import VideoRecording
    from django.core.paginator import Paginator
    from django.views.decorators.csrf import csrf_exempt
    from .forms import AudioInteractiveForm, ChoiceCreateForm
    from django.contrib import messages
    from django.utils import timezone
    import os, pytz
    from .models import Call
    from django.http import HttpResponse
    from django.contrib.auth.models import User
    import threading
    import time
    from users.tfa import send_user_text
    import datetime
    from django.conf import settings
    from .models import AudioInteractive
    hidenavbar = False
    if request.GET.get('hidenavbar', False):
        hidenavbar = True
    if request.method == "POST":
        form = ChoiceCreateForm(request.POST)
        form.instance.user = request.user
        form.save()
        messages.success(request, 'The option, {}, has been saved.'.format(form.instance.option))
    return render(request, 'voice/add_option.html', {'form': ChoiceCreateForm(), 'hidenavbar': hidenavbar, 'small': True})

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def recordings(request):
    from django.shortcuts import render
    from django.contrib.auth.decorators import login_required
    from django.shortcuts import redirect, get_object_or_404
    from django.urls import reverse
    from django.utils import timezone
    from django.contrib.auth.decorators import user_passes_test
    from vendors.tests import is_vendor
    from feed.tests import identity_verified
    from vendors.tests import is_vendor
    from django.contrib.sessions.models import Session
    from live.models import VideoRecording
    from django.core.paginator import Paginator
    from django.views.decorators.csrf import csrf_exempt
    from .forms import AudioInteractiveForm, ChoiceCreateForm
    from django.contrib import messages
    from django.utils import timezone
    import os, pytz
    from .models import Call
    from django.http import HttpResponse
    from django.contrib.auth.models import User
    import threading
    import time
    from users.tfa import send_user_text
    import datetime
    from django.conf import settings
    from .models import AudioInteractive
    page = 1
    if(request.GET.get('page', '') != ''):
        page = int(request.GET.get('page', ''))
    recordings = AudioInteractive.objects.filter(user=request.user).order_by('-uploaded_file')
    p = Paginator(recordings, 10)
    if page > p.num_pages or page < 1:
        messages.warning(request, "The page you requested, " + str(page) + ", does not exist. You have been redirected to the first page.")
        page = 1
    return render(request, 'voice/interactives.html', {
        'title': 'Voice Recording Interactive Files',
        'recordings': p.page(page),
        'count': p.count,
        'page_obj': p.get_page(page),
    })

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def recording(request, id):
    from django.shortcuts import render
    from django.contrib.auth.decorators import login_required
    from django.shortcuts import redirect, get_object_or_404
    from django.urls import reverse
    from django.utils import timezone
    from django.contrib.auth.decorators import user_passes_test
    from vendors.tests import is_vendor
    from feed.tests import identity_verified
    from vendors.tests import is_vendor
    from django.contrib.sessions.models import Session
    from live.models import VideoRecording
    from django.core.paginator import Paginator
    from django.views.decorators.csrf import csrf_exempt
    from .forms import AudioInteractiveForm, ChoiceCreateForm
    from django.contrib import messages
    from django.utils import timezone
    import os, pytz
    from .models import Call
    from django.http import HttpResponse
    from django.contrib.auth.models import User
    import threading
    import time
    from users.tfa import send_user_text
    import datetime
    from django.conf import settings
    from .models import AudioInteractive
    recording = None
    try:
        recording = AudioInteractive.objects.get(id=int(id))
    except:
        recording = None
    if request.method == 'POST':
        try:
            recording = AudioInteractive.objects.get(id=int(id))
        except:
            recording = AudioInteractive.objects.create(user=request.user)
        audio_interactive_form = AudioInteractiveForm(request.POST, request.FILES, instance=recording)
        audio_interactive_form.instance.user = request.user
        if request.FILES:
            audio_interactive_form.instance.uploaded_file = timezone.now()
        if audio_interactive_form.is_valid():
            recording = audio_interactive_form.save()
            from tts.slice import convert_wav
            path = convert_wav(recording.content.path)
            recording.content = path
            recording.save()
            messages.success(request, 'You have updated this recording\'s interactive to \"{}\".'.format(audio_interactive_form.instance.interactive))
        else:
            print('The form is invalid')
    audio_interactive_form = AudioInteractiveForm(instance=recording)
    return render(request, 'voice/interactive.html', {'title': 'Voice Recording', 'recording': recording, 'form': audio_interactive_form})

@csrf_exempt
def voice(request):
    from django.shortcuts import render
    from django.contrib.auth.decorators import login_required
    from django.shortcuts import redirect, get_object_or_404
    from django.urls import reverse
    from django.utils import timezone
    from django.contrib.auth.decorators import user_passes_test
    from vendors.tests import is_vendor
    from feed.tests import identity_verified
    from vendors.tests import is_vendor
    from django.contrib.sessions.models import Session
    from live.models import VideoRecording
    from django.core.paginator import Paginator
    from django.views.decorators.csrf import csrf_exempt
    from .forms import AudioInteractiveForm, ChoiceCreateForm
    from django.contrib import messages
    from django.utils import timezone
    import os, pytz
    from .models import Call
    from django.http import HttpResponse
    from django.contrib.auth.models import User
    import threading
    import time
    from users.tfa import send_user_text
    import datetime
    from django.conf import settings
    from .models import AudioInteractive
    from twilio.twiml.messaging_response import MessagingResponse
    from twilio.twiml.voice_response import VoiceResponse, Gather
    from twilio.rest import Client
    from_phone = User.objects.get(id=settings.MY_ID).profile.phone_number
    phone = request.POST.get('From', '')
    session_id = request.GET.get('SessionID')
    user = None
    users = User.objects.filter(profile__phone_number=phone).order_by('-profile__last_seen')
    if users.count() > 0:
        user = users.first()
    if phone == '+1': user = None
    resp = VoiceResponse()
    client = Client(account_sid, auth_token)
    if request.POST.get('SpeechResult') or request.POST.get('UnstableSpeechResult'):
        speech = request.POST.get('SpeechResult', '') if request.POST.get('SpeechResult', False) else request.POST.get('UnstableSpeechResult', '')
        l = speech.lower()
        from voice.ai import get_ai_response, post_ai_response
        text_nl = get_ai_response(speech)
        if user and user.profile.vendor:
            from autocorrect import Speller
            spell = Speller(lang=settings.DEFAULT_LANG)
            post_ai_response(user, spell(speech.capitalize()) + '\n\n' + text_nl)
        text = text_nl.replace('\n', ' ')
        if user and hasattr(user, 'voice_profile'):
            user.voice_profile.call_logs = user.voice_profile.call_logs + speech + '***' + text + '***'
            user.voice_profile.save()
        resp.say(text, voice='alice')
        gather = Gather(input='speech', timeout=15, action=reverse('voice:voice'))
        gather.say('What else can I help you with?', voice='alice')
        resp.append(gather)
        resp.redirect(reverse('voice:voice'))
        return HttpResponse(str(resp), content_type='text/xml')
    if request.POST.get('Digits'):
        choice = request.POST.get('Digits')
        if user and hasattr(user, 'voice_profile'):
            Call.objects.create(user=user, sid=session_id)
            if user.voice_profile.last_call and user.voice_profile.recordings:
                if timezone.now() - datetime.timedelta(minutes=1) < user.voice_profile.last_call:
                    interactives = AudioInteractive.objects.filter(label=user.voice_profile.interactive)
                    interact = None
                    if interactives.count() > 0:
                        interact = interactives.first()
                    else:
                        interact = AudioInteractive.objects.get(label='init')
                    for option in interact.choices.all():
                        if choice == str(option.number):
                            interactives = AudioInteractive.objects.filter(label=option.option)
                            interact = None
                            if interactives.count() > 0:
                                interact = interactives.first()
                            else:
                                interact = AudioInteractive.objects.get(label='init')
                            gather = Gather(num_digits=1, timeout=30)
                            gather.play(interactive(interact.label))
                            user.voice_profile.interactive = interact.label
                            user.voice_profile.save()
                            if interact.label == 'call':
                                resp.dial(from_phone)
                            else:
                                resp.append(gather)
                            return HttpResponse(str(resp), content_type='text/xml')
            user.voice_profile.last_call = timezone.now()
            user.voice_profile.save()
        if choice == '1':
            resp.play(interactive('call'))
            resp.dial(from_phone)
            return HttpResponse(str(resp), content_type='text/xml')
        elif choice == '2':
            resp.play(interactive('callback'))
            return HttpResponse(str(resp), content_type='text/xml')
        elif choice == '3':
            resp.play(interactive('recording'))
            return HttpResponse(str(resp), content_type='text/xml')
        elif choice == '4':
            resp.play(interactive('recordings'))
            gather = Gather(num_digits=1, timeout=30)
            gather.play(interactive('init'))
            resp.append(gather)
            user.voice_profile.recordings = True
            user.voice_profile.interactive = 'init'
            user.voice_profile.last_call = timezone.now()
            user.voice_profile.save()
            return HttpResponse(str(resp), content_type='text/xml')
        elif choice == '5':
            resp.play(interactive('record'))
            resp.record()
        elif choice == '6':
            gather = Gather(input='speech', timeout=15, action=reverse('voice:voice'))
            gather.say('What else do you need? Talk to me, or ask me a question.', voice='alice')
            resp.append(gather)
            resp.redirect(reverse('voice:voice'))
        else:
            resp.play(interactive('sorry'))
            resp.redirect(reverse('voice:voice'))
            return HttpResponse(str(resp), content_type='text/xml')
    called = False
    if user:
        if hasattr(user, 'voice_profile'):
            resp.play(interactive('hello'))
            resp.say(user.profile.name if user else 'guest', voice='alice')
            if user.voice_profile.last_call:
                if timezone.now() - datetime.timedelta(minutes=1) < user.voice_profile.last_call:
                    resp.play(interactive('recent call'))
                    called = True
            resp.play(interactive('thanks'))
        if hasattr(user, 'voice_profile'):
            user.voice_profile.last_call = timezone.now()
            user.voice_profile.recordings = False
            user.voice_profile.save()
        resp.play(interactive('verified'))
        gather = Gather(num_digits=1, timeout=30)
        gather.play(interactive('select'))
        resp.append(gather)
    elif not user:
        resp.play(interactive('signup'))
    return HttpResponse(str(resp), content_type='text/xml')
