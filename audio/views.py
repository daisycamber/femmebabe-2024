from django.contrib.auth.decorators import login_required
from feed.tests import identity_verified
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.cache import never_cache, cache_page
from vendors.tests import is_vendor
from feed.tests import identity_verified
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import patch_cache_control
from django.views.decorators.vary import vary_on_cookie
import threading, time, pytz, shutil, datetime

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def add_post(request, id):
    from feed.models import Post
    from .models import AudioRecording
    from django.shortcuts import redirect, get_object_or_404
    audio = get_object_or_404(AudioRecording, id=id)
    if request.method == 'POST':
        from .models import get_file_path
        audio_feed = request.GET.get('feed') if request.GET.get('feed', None) else 'samples'
        path = os.path.join(settings.MEDIA_ROOT, get_file_path(audio, audio.content.name))
        shutil.copy(audio.content.path, path)
        post = Post.objects.create(author=request.user, public=True, private=False, published=True, paid_file=True, price='5', feed=audio_feed, file=path, content=audio.notes + ' - ' + audio.transcript)
        return redirect(reverse('feed:post-detail', kwargs={'uuid': post.uuid}))

@csrf_exempt
@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def publish(request, id):
    from django.shortcuts import get_object_or_404
    from .models import AudioRecording
    audio = get_object_or_404(AudioRecording, id=id)
    if request.method == 'POST':
        audio.public = not audio.public
        audio.save()
        from django.http import HttpResponse
        if audio.public:
            return HttpResponse('Public')
        else:
            return HttpResponse('Private')

@csrf_exempt
@never_cache
@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def confirm(request, id):
    from .models import AudioRecording
    from django.http import HttpResponse
    import datetime
    return HttpResponse('y' if AudioRecording.objects.filter(confirmation_id=id, uploaded_file__gte=timezone.now() - datetime.timedelta(minutes=5)).count() > 0 else 'n')

@vary_on_cookie
@cache_page(60)
def recordings(request):
    from django.contrib.auth.models import User
    from .models import AudioRecording
    from django.urls import reverse
    from django.contrib import messages
    from django.core.paginator import Paginator
    from django.shortcuts import redirect, render
    theuser = User.objects.filter(profile__name=request.GET.get('model', '')).first()
    recordings = None
    recordings = AudioRecording.objects.filter(user=theuser, public=True).order_by('-uploaded_file')
    if not theuser and request.user.is_authenticated and request.user.profile.vendor:
        theuser = request.user
        recordings = AudioRecording.objects.filter(user=request.user).order_by('-uploaded_file')
    elif not theuser:
        messages.warning(request, 'The user matching your query does not exist.')
        return redirect(reverse('landing:landing'))
    page = 1
    if(request.GET.get('page', '') != ''):
        page = int(request.GET.get('page', ''))
    p = Paginator(recordings, 10)
    if page > p.num_pages or page < 1:
        messages.warning(request, "The page you requested, " + str(page) + ", does not exist. You have been redirected to the first page.")
        page = 1
    r = render(request, 'audio/recordings.html', {
        'title': 'Audio Recordings',
        'recordings': p.page(page),
        'count': p.count,
        'page_obj': p.get_page(page),
        'theuser': theuser
    })
    if request.user.is_authenticated: patch_cache_control(r, private=True)
    else: patch_cache_control(r, public=True)
    return r

@csrf_exempt
@cache_page(60*60*24*30)
def recording(request, id):
    from django.utils import timezone
    from .models import AudioRecording
    from django.contrib import messages
    from django.shortcuts import render, redirect
    from django.urls import reverse
    from .forms import AudioRecordingForm
    from django.conf import settings
    try:
        recording = AudioRecording.objects.get(id=int(id))
    except:
        recording = None
    theuser = recording.user if recording else None
    if request.user.is_authenticated and not theuser and request.user.profile.vendor:
        theuser = request.user
    elif not theuser and request.user.is_authenticated:
        messages.warning(request, 'The user matching your query does not exist.')
        return redirect(reverse('landing:landing'))
#    elif not request.user.profile.vendor:
#        if not theuser in request.user.profile.subscriptions.all():
#            raise PermissionDenied()
    recording = None
    if request.user.is_authenticated and theuser == request.user and request.user.profile.vendor and request.method == 'POST' and (not recording or request.user == recording.user):
        from tts.slice import process_user_audio
        from .transcription import get_transcript
        from audio.fingerprinting import save_fingerprint, is_in_database
        import os
        from django.conf import settings
        from .models import get_file_path
        from django.http import HttpResponse
        audio_form = AudioRecordingForm(request.POST, request.FILES)
        audio_form.instance.user = request.user
        print('Is audio form valid? ' + str(audio_form.errors))
        if audio_form.is_valid():
            if request.FILES:
                import shutil
                print('Request has files.')
                audio_form.instance.uploaded_file = timezone.now()
                recording = audio_form.save()
                path = os.path.join(settings.MEDIA_ROOT, get_file_path(recording, recording.content.name))
                shutil.copy(recording.content.path, path)
                recording.content_backup = path
                recording.save()
                pd = True
                for p in recording.pitch_notes.split(','):
                    if p != 'NaN':
                        pd = False
                if pd:
                    recording.pitch_detect()
                try:
                    if request.POST.get('generate_transcript'):
                        recording.transcript, recording.fingerprint = get_transcript(recording.content.path)
                    else:
                        recording.transcript = 'transcription disabled for this audio.'
                    if not recording.fingerprint: recording.fingerprint = save_fingerprint(path)
                    recording.save()
                    if request.POST.get('generate_speech'):
                        process_user_audio(request.user, recording, recording.content.path)
                except: pass
                if not request.POST.get('live'): messages.success(request, 'You have saved this recording.')
                similar = is_in_database(recording.fingerprint)
                if recording.post:
                    from feed.models import Post
                    audio_feed = request.GET.get('feed') if request.GET.get('feed', None) else 'samples'
                    path = os.path.join(settings.MEDIA_ROOT, get_file_path(recording, recording.content.name))
                    shutil.copy(recording.content.path, path)
                    post = Post.objects.create(author=request.user, public=True, private=False, published=True, posted=True, paid_file=True, price='5', feed=audio_feed, file=path, content=recording.notes + ' - ' + recording.transcript)
                return HttpResponse('Saved.' if not similar else 'Similar, {}'.format('' + str(AudioRecording.objects.filter(fingerprint__in=fingerprints).order_by('-uploaded_file')))) #reverse('audio:record', kwargs={'id': recording.id}))
    recording = None
    try:
        recording = AudioRecording.objects.get(id=int(id))
    except:
        recording = None
    audio_form = AudioRecordingForm(instance=recording, initial={'live': request.GET.get('live', False), 'generate_speech': request.GET.get('speech', False), 'generate_transcript': request.GET.get('transcript', False),})
    from django.core.exceptions import PermissionDenied
    if recording and not recording.public and not recording.user == theuser:
        raise PermissionDenied()
    if request.user.is_authenticated and not recording and not request.user.profile.vendor:
        raise PermissionDenied()
    import pytz
    r = render(request, 'audio/recording.html', {'title': 'Voice Recording', 'recording': recording, 'form': audio_form, 'current_time_js': timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%a %b %d %Y %H:%M:%S GMT-0700 (Pacific Daylight Time)'), 'preload': True, 'load_timeout': 3000, 'theuser': theuser, 'pitches_per_second': settings.PITCHES_PER_SECOND, 'target_pitch': settings.TARGET_PITCH, 'max_pitch': settings.MAX_PITCH})
    if request.user.is_authenticated: patch_cache_control(r, private=True)
    else: patch_cache_control(r, public=True)
    return r

