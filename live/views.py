from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test
from feed.tests import identity_verified
from vendors.tests import is_vendor
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import User

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def choose_live_camera(request):
    from .forms import ChooseCameraForm
    from django.shortcuts import redirect
    from django.urls import reverse
    if request.method == 'POST':
        form = ChooseCameraForm(request.POST)
        if form.is_valid():
            return redirect(reverse('live:golivevideo') + '?camera={}'.format(form.cleaned_data.get('choice')))
    from django.shortcuts import render
    return render(request, 'live/choose_camera.html', {'title': 'Choose Camera', 'form': ChooseCameraForm()})


@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def choose_camera(request):
    from .forms import ChooseCameraForm
    from django.shortcuts import redirect
    from django.urls import reverse
    if request.method == 'POST':
        form = ChooseCameraForm(request.POST)
        if form.is_valid() and form.cleaned_data.get('choice') != '':
            return redirect(reverse('live:name-camera') + '?camera=' + form.cleaned_data.get('choice'))
    from django.shortcuts import render
    return render(request, 'live/choose_camera.html', {'title': 'Choose Camera', 'form': ChooseCameraForm()})

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def name_camera(request):
    from .forms import NameCameraForm
    from django.shortcuts import redirect
    from django.urls import reverse
    from .models import VideoCamera
    from django.contrib import messages
    name = request.GET.get('camera')
    cameras = VideoCamera.objects.filter(user=request.user, name=name)
    if not cameras.first() and name != '': VideoCamera.objects.create(user=request.user, name=name)
    elif not cameras.first(): cameras = VideoCamera.objects.filter(user=request.user).order_by('-last_frame')
    camera = cameras.first()
    if request.method == 'POST':
        form = NameCameraForm(request.POST, instance=camera)
        if form.is_valid() and form.instance.name != '' and VideoCamera.objects.filter(user=request.user, name=form.instance.name).count() > 0:
            camera = form.save()
            messages.success(request, 'The camera, {}, was updated.'.format(camera.name))
            return redirect(request.path + '?camera={}'.format(camera.name))
    from django.shortcuts import render
    return render(request, 'live/name_camera.html', {'title': 'Update Camera {}'.format(camera.name), 'form': NameCameraForm(instance=camera), 'camera': camera})


@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def shows(request):
    from .models import Show
    shows = Show.objects.filter(model=request.user, end__gte=timezone.now()).order_by('start')
    from django.shortcuts import render
    return render(request, 'live/shows.html', {
        'title': 'Live Shows',
        'shows': shows,
        'count': len(shows),
    })

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@csrf_exempt
def book_show(request, username):
    from django.contrib.auth.models import User
    from django.contrib import messages
    from django.shortcuts import redirect
    from django.urls import reverse
    from .forms import LiveShowForm
    model = User.objects.get(profile__name=username)
    if (not model in request.user.profile.subscriptions.all()):
        messages.warning(request, 'You need to follow {} before you can book a show.'.format(username))
        return redirect(reverse('feed:follow', kwargs={'username': username}))
    form = LiveShowForm(request.POST, instance=model.profile)
    if request.method == 'POST':
        from .models import Show
        import datetime
        from django.conf import settings
        from users.tfa import send_user_text
        from django.utils import timezone
        import pytz
        if form.is_valid():
            time = datetime.datetime.strptime(form.cleaned_data.get('choice'), '%m/%d/%Y %H:%M:%S').astimezone(pytz.timezone(settings.TIME_ZONE))
            model_count = Show.objects.filter(model=model, start__gte=timezone.now(), end__lte=timezone.now() + datetime.timedelta(hours=24 * 7)).count()
            user_count = Show.objects.filter(user=request.user, start__gte=timezone.now(), end__lte=timezone.now() + datetime.timedelta(hours=24 * 7)).count()
            if time > timezone.now() + datetime.timedelta(minutes=settings.SHOW_BOOK_OUT_MINUTES) and not Show.objects.filter(start__gte=time, end__lte=time + datetime.timedelta(minutes=settings.LIVE_SHOW_LENGTH_MINUTES)) and user_count < settings.SHOWS_PER_USER_WEEK and model_count < settings.SHOWS_PER_VENDOR_WEEK:
                Show.objects.create(user=request.user, model=model, start=time, end=time+datetime.timedelta(minutes=settings.LIVE_SHOW_LENGTH_MINUTES))
                send_user_text(model, '@{} has scheduled a show with you at {}'.format(request.user, form.cleaned_data.get('choice')))
                messages.success(request, 'You have scheduled this live show. Please make a note somewhere. You will see me {}'.format(form.cleaned_data.get('choice')))
                return redirect(reverse('feed:profile', kwargs={'username': model.profile.name}))
    from django.shortcuts import render
    return render(request, 'live/book_show.html', {
        'title': 'Book a live show',
        'form': form,
        'model': model
    })

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def still(request, filename):
    from django.core.exeptions import PermissionDenied
    import os
    from django.http import Http404
    from django.conf import settings
    u = int(filename.split('.')[0].split('-')[-1])
    if u != request.user.id:
        raise PermissionDenied()
    try:
        image_data = open(os.path.join(settings.BASE_DIR, 'media/secure/video/', filename), "rb").read()
    except:
        raise Http404
    ext = filename.split('.')[1]
    from django.http import HttpResponse
    return HttpResponse(image_data, content_type="image/{}".format(ext))

def file_iterator(file_name, chunk_size=8192, offset=0, length=None):
  with open(file_name, "rb") as f:
    f.seek(offset, os.SEEK_SET)
    remaining = length
    while True:
      bytes_length = chunk_size if remaining is None else min(remaining, chunk_size)
      data = f.read(bytes_length)
      if not data:
        break
      if remaining:
        remaining -= len(data)
      yield data


@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@csrf_exempt
def stream_secure_video(request, filename):
  u = int(filename.split('.')[0].split('-')[-1])
  if u != request.user.id:
    from django.core.exceptions import PermissionDenied
    raise PermissionDenied()
  import os, re
  from django.http import StreamingHttpResponse
  from django.conf import settings
  path = os.path.join(settings.BASE_DIR,'media/secure/video/', filename)
  """Responding to the video file by streaming media"""
  range_header = request.META.get('HTTP_RANGE', '').strip()
  range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)
  range_match = range_re.match(range_header)
  size = os.path.getsize(path)
  content_type, encoding = mimetypes.guess_type(path)
  content_type = content_type or 'application/octet-stream'
  if range_match:
    first_byte, last_byte = range_match.groups()
    first_byte = int(first_byte) if first_byte else 0
    last_byte = first_byte + 1024 * 1024 * 8    # 8M Each piece, the maximum volume of the response body
    if last_byte >= size:
      last_byte = size - 1
    length = last_byte - first_byte + 1
    resp = StreamingHttpResponse(file_iterator(path, offset=first_byte, length=length), status=206, content_type=content_type)
    resp['Content-Length'] = str(length)
    resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
  else:
    # When it is not obtained by video stream, the entire file is returned by generator to save memory
    from wsgiref.util import FileWrapper
    resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')), content_type=content_type)
    resp['Content-Length'] = str(size)
  resp['Accept-Ranges'] = 'bytes'
  return resp

#@login_required
#@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@csrf_exempt
def video_frame(request, username):
  from users.models import Profile
  from .models import VideoCamera
  from django.contrib.auth.models import User
  profile = get_object_or_404(Profile, name=username, identity_verified=True, vendor=True)
  cameras = VideoCamera.objects.filter(user=profile.user, name=request.GET.get('camera'))
  model = User.objects.get(profile__name=username)
#  if request.user != model and (not is_live_show(request, model) or (not model in request.user.profile.subscriptions.all())):
#    messages.warning(request, 'You need to follow {} before you can see their interactive feed.'.format(username))
#    return redirect(reverse('feed:follow', kwargs={'username': username}))
  c = cameras.first()
  init = int(request.GET.get('index')) - (camera.frames.count() - camera.frame_count)
  frame = c.frames.filter(processed=True, public=True if profile.user != request.user else None).order_by('time_captured')[int(request.GET.get('index')) if not camera.default else -1]
  filename = frame.name.split('/')[-1]
  from django.http import HttpResponse
  return HttpResponse(reverse('live:stream-video', kwargs={'filename': filename}))

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@csrf_exempt
def stream_video(request, filename):
  import os, re
  from django.http import StreamingHttpResponse
  from django.conf import settings
  path = os.path.join(settings.BASE_DIR,'media/live/files/', filename)
  """Responding to the video file by streaming media"""
  range_header = request.META.get('HTTP_RANGE', '').strip()
  range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)
  range_match = range_re.match(range_header)
  size = os.path.getsize(path)
  content_type, encoding = mimetypes.guess_type(path)
  content_type = content_type or 'application/octet-stream'
  if range_match:
    first_byte, last_byte = range_match.groups()
    first_byte = int(first_byte) if first_byte else 0
    last_byte = first_byte + 1024 * 1024 * 8    # 8M Each piece, the maximum volume of the response body
    if last_byte >= size:
      last_byte = size - 1
    length = last_byte - first_byte + 1
    resp = StreamingHttpResponse(file_iterator(path, offset=first_byte, length=length), status=206, content_type=content_type)
    resp['Content-Length'] = str(length)
    resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
  else:
    from wsgiref.util import FileWrapper
    # When it is not obtained by video stream, the entire file is returned by generator to save memory
    resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')), content_type=content_type)
    resp['Content-Length'] = str(size)
  resp['Accept-Ranges'] = 'bytes'
  return resp

def remote_api(request):
    from .models import VideoCamera
    from django.utils import timezone
    from django.http import HttpResponse
    from django.core.exceptions import PermissionDenied
    camera = None
    if request.user.is_authenticated:
        camera, created = VideoCamera.objects.get_or_create(user=request.user, name=request.GET.get('camera'))
    else:
        camera = VideoCamera.objects.get(key=request.GET.get('key', None))
        camera.updated = timezone.now()
        camera.save()
    if not identity_verified(camera.user): raise PermissionDenied()
    return HttpResponse('r' if camera.live else 'x')

LIVE_UPDATE_SECONDS = 1

@csrf_exempt
@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def remote(request):
    from .models import VideoCamera
    import datetime
    from django.utils import timezone
    from django.http import HttpResponse
    cameras = VideoCamera.objects.filter(user=request.user, name=request.GET.get('camera'))
    camera = cameras.first()
    if request.method == 'POST':
        if not camera.updated > timezone.now() - datetime.timedelta(seconds=LIVE_UPDATE_SECONDS):
            camera.live = not camera.live
            camera.updated = timezone.now()
            camera.save()
    return HttpResponse('<i class="bi bi-toggle-on"></i>' if camera.live else '<i class="bi bi-toggle-off"></i>')

def mute(request):
    from .models import VideoCamera
    from django.http import  HttpRepsonse
    from django.utils import timezone
    import datetime
    cameras = VideoCamera.objects.filter(user__profile__name=request.GET.get('user', None), name=request.GET.get('camera'), key=request.GET.get('key', ''))
    camera = cameras.first()
    if request.method == 'POST':
        if not camera.updated > timezone.now() - datetime.timedelta(seconds=LIVE_UPDATE_SECONDS):
            camera.mute = not camera.mute
            camera.updated = timezone.now()
            camera.save()
    return HttpResponse('<i class="bi bi-mic-fill"></i>' if camera.muted else '<i class="bi bi-mic-muted"></i>')

@csrf_exempt
@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def record_remote(request):
    from .models import VideoCamera
    import datetime
    from django.util import timezone
    cameras = VideoCamera.objects.filter(user=request.user, name=request.GET.get('camera'))
    camera = cameras.first()
    if request.method == 'POST':
        if not camera.updated > timezone.now() - datetime.timedelta(seconds=LIVE_UPDATE_SECONDS):
            camera.recording = not camera.recording
            camera.updated = timezone.now()
            camera.save()
    print('Toggling camera recording status.')
    from django.shortcuts import render
    return HttpResponse('<i class="bi bi-toggle-on"></i>' if camera.recording else '<i class="bi bi-toggle-off"></i>')

def confirm(request, id):
    from django.http import HttpResponse
    from .models import VideoFrame
    from django.utils import timezone
    import datetime
    return HttpResponse('y' if VideoFrame.objects.filter(confirmation_id=id, time_captured__gte=timezone.now() - datetime.timedelta(minutes=5)).count() > 0 or VideoCamera.objects.filter(confirmation_id=id, time_captured__gte=timezone.now() - datetime.timedelta(minutes=5)).count() > 0 else 'n')


@csrf_exempt
def golivevideo(request):
    from .models import VideoCamera, VideoFrame, VideoRecording
    from django.core.exceptions import PermissionDenied
    from .forms import CameraForm
    import datetime
    import pytz
    from django.utils import timezone
    from django.http import HttpResponse
    from django.conf import settings
    from lotteh.celery import delay_remove_frame
    name = request.GET.get('camera')
    if not name:
        name = 'private'
    camera = None
    if request.user.is_authenticated:
        camera, created = VideoCamera.objects.get_or_create(user=request.user, name=name)
    else:
        camera = VideoCamera.objects.get(key=request.GET.get('key', None)) #, recording=False)
        if not camera.user.profile.vendor: raise PermissionDenied()
    if not identity_verified(camera.user): raise PermissionDenied()
    if request.method == 'POST':
        import shutil
        from .still import get_still, is_still
        try:
            form = CameraForm(request.POST, request.FILES, instance=camera)
            if not form.is_valid(): print(form.errors)
            form.instance.last_frame = timezone.now()
            form.instance.confirmation_id = form.cleaned_data.get('confirmation_id', '')
            timestamp = datetime.datetime.fromtimestamp(int(form.cleaned_data.get('timestamp')) / 1000, tz=pytz.UTC)
            camera = form.save()
            recording = None
            is_frame_still, error = is_still(camera.frame.path)
            if camera.recording and not is_frame_still:
                show = Show.objects.filter(start__lte=timezone.now() + datetime.timedelta(minutes=settings.LIVE_SHOW_LENGTH_MINUTES), start__gte=timezone.now()).first()
                recordings = VideoRecording.objects.filter(user=camera.user, camera=camera.name, public=False if Show.objects.filter(start__lte=timezone.now() + datetime.timedelta(minutes=settings.LIVE_SHOW_LENGTH_MINUTES), start__gte=timezone.now()).count() > 0 else True, recipient=show.user if show else None)
                if recordings.count() == 0:
                    recording = VideoRecording.objects.create(user=camera.user, camera=camera.name, last_frame=timestamp, public=False if Show.objects.filter(start__lte=timestamp + datetime.timedelta(minutes=settings.LIVE_SHOW_LENGTH_MINUTES), start__gte=timezone.now()).count() > 0 else True, recipient=show.user if show else None)
                    recording.save()
                else:
                    recording = recordings.last()
                if recording.last_frame < timezone.now() - datetime.timedelta(seconds=int(settings.LIVE_INTERVAL/1000 * 3)) or (recording.frames.first() and ((recording.last_frame - recording.frames.first().time_captured).total_seconds() > settings.RECORDING_LENGTH_SECONDS)):
                    recording = VideoRecording.objects.create(user=camera.user, camera=camera.name, last_frame=timestamp, public=False if Show.objects.filter(start__lte=timezone.now() + datetime.timedelta(minutes=settings.LIVE_SHOW_LENGTH_MINUTES), start__gte=timezone.now()).count() > 0 else True, recipient=show.user if show else None)
                    recording.compressed = camera.compress_video
                    recording.save()
            path = os.path.join(settings.BASE_DIR, 'media/', get_file_path(camera, camera.frame.name))
            shutil.copy(camera.frame.path, path)
            frame = VideoFrame.objects.create(user=camera.user, frame=path, compressed=camera.compress_video, time_captured=timestamp, confirmation_id=form.cleaned_data.get('confirmation_id', ''), difference=error)
            frame.save()
            if not camera.recording or is_frame_still:
                delay_remove_frame.apply_async([frame.id], countdown=int(settings.LIVE_INTERVAL/1000*4))
            camera.frames.add(frame)
            camera.frame_count = camera.frame_count + 1
            camera.mime = frame.frame.name.split('.')[1]
            camera.save()
            if recording:
                recording.frames.add(frame)
                recording.last_frame = timestamp
                recording.save()
                process_recording.apply_async([recording.id], countdown=settings.LIVE_INTERVAL/1000 * 3)
            else: print('Not saving frame')
            process_live.apply_async([camera.id, frame.id], countdown=settings.LIVE_INTERVAL/1000 * 3)
            print('5 second video uploaded')
            return HttpResponse(status=200)
        except:
            print(traceback.format_exc())
        return HttpResponse(status=200)
    if camera.last_frame > timezone.now() - datetime.timedelta(seconds=settings.LIVE_INTERVAL/1000*2):
        return redirect(request.path + '?camera=camera'.format(random.randint(1,99)))
    if not request.GET.get('disable'):
        camera.live = True
        camera.save()
    from django.utils.crypto import get_random_string
    camera_key = get_random_string(length=settings.CAMERA_KEY_LENGTH)
    camera.key = camera_key
    camera.save()
    from django.shortcuts import redirect
    from django.urls import reverse
    if not request.user.is_authenticated: return redirect(reverse('users:login'))
    from django.shortcuts import render
    return render(request, 'live/golivevideo.html', {'title': 'Go Live', 'camera': camera, 'full': True, 'form': CameraForm(), 'preload': True, 'load_timeout': 5000, 'should_compress_live': request.user.vendor_profile.compress_video, 'key': camera_key, 'use_websocket': camera.use_websocket})

#@login_required
#@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@csrf_exempt
def livevideo(request, username):
    from django.contrib.auth.models import User
    from django.contrib import messages
    from django.urls import reverse
    from django.shortcuts import redirect
    from users.models import Profile
    from security.middleware import get_qs
    from django.shortcuts import get_object_or_404
    import datetime
    from django.utils import timezone
    from live.show import is_live_show, get_live_show
    from live.models import VideoCamera
    from django.conf import settings
    model = User.objects.get(profile__name=username)
    if not request.GET.get('key') and not model == request.user and is_live_show(request, model) and hasattr(request, 'user') and get_live_show(request, model) and get_live_show(request, model).user != request.user:
        messages.warning(request, '{} is in a live show with someone else right now. Please book a private show.'.format(username))
        return redirect(reverse('live:book-live-show', kwargs={'username': username}) + get_qs(request.GET))
    if not request.GET.get('key') and not model == request.user and request.GET.get('camera', None) and request.GET.get('camera') != 'private':
        messages.warning(request, 'You need to follow {} before you can see their live show.'.format(username))
        return redirect(reverse('feed:follow', kwargs={'username': username}) + get_qs(request.GET))
    hidenav = None
    if request.GET.get('hidenavbar','') != '':
        hidenav = True
    profile = get_object_or_404(Profile, name=username, identity_verified=True, vendor=True)
    cameras = VideoCamera.objects.filter(user=profile.user, name=request.GET.get('camera') if request.GET.get('camera') else 'private')
    camera = cameras.first()
    if camera and request.GET.get('key') and camera.key != request.GET.get('key') and not camera.public:
        return redirect(reverse('feed:follow', kwargs={'username': username}) + get_qs(request.GET))
    if not cameras.first() or not cameras.first().last_frame > timezone.now() - datetime.timedelta(seconds=settings.LIVE_INTERVAL/1000*3):
        messages.warning(request, '{}\'s camera is not active. Consider booking a show.'.format(username))
        return redirect(reverse('live:book-live-show', kwargs={'username': username}) + get_qs(request.GET)) if hasattr(request, 'user') and request.user.is_authenticated else redirect(reverse('feed:follow', kwargs={'username': username}) + get_qs(request.GET))
    from django.shortcuts import render
    return render(request, 'live/livevideo.html', {'profile': profile, 'camera': cameras.first(), 'title': 'Live Video', 'hidenavbar': hidenav, 'should_compress_live': model.vendor_profile.compress_video})

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@csrf_exempt
def last_frame_video(request, username):
    from .models import VideoCamera
    from django.shortcuts import get_object_or_404
    from users.models import Profile
    profile = get_object_or_404(Profile, name=username, identity_verified=True, vendor=True)
    cameras = VideoCamera.objects.filter(user=profile.user, name=request.GET.get('camera'))
    return render(request, 'live/lastframe.html', {'profile': profile, 'camera': cameras.first(), 'frame': camera.frames.all().last()})
