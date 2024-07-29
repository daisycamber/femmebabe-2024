from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from vendors.tests import is_vendor
from feed.tests import identity_verified

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def projects(request):
    from django.shortcuts import render
    from .models import Project
    from django.core.paginator import Paginator
    projects = Project.objects.filter(user=request.user).order_by('-last_updated')
    p = Paginator(projects, 10)
    if page > p.num_pages or page < 1:
        messages.warning(request, "The page you requested, " + str(page) + ", does not exist. You have been redirected to the first page.")
        page = 1
    return render(request, 'synthesizer/projects.html', {'title': 'Audio Projects', 'projects': projects, 'page_obj': p.get_page(page), 'count': p.count})

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def project(request, id):
    from django.shortcuts import render
    from .models import Project
    from django.urls import reverse
    from django.utils import timezone
    project = None
    if id == 'new':
        project = Project.objects.create(user=request.user, name='New Project {}'.format(timezone.now().strftime('%B%d%Y')))
    else:
        project = Project.objects.filter(user=request.user, identifier=id).first()
        if not project:
            project = Project.objects.create(user=request.user, name='New Project {}'.format(timezone.now().strftime('%B%d%Y')))
    return render(request, 'synthesizer/project.html', {'title': 'Edit Project'.format(project.name), 'project': project, 'init_instrument': project.synths.all()[project.instrument]})

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def audio_recording(request, id):
    from django.shortcuts import render
    from audio.models import AudioRecording
    from django.shortcuts import redirect, get_object_or_404
    from django.urls import reverse
    from django.core.exceptions import PermissionDenied
    from .forms import EditAudioForm
    import os, shutil
    from django.utils import timezone
    from django.conf import settings
    from audio.models import get_file_path
    from django.core.paginator import Paginator
    from tts.slice import convert_wav
    from .plot import visualize
    from pydub import AudioSegment, effects
    from .utils import add_reverb, adjust_pitch, compressor, highpass_filter, lowpass_filter, gain
    recording = get_object_or_404(AudioRecording, id=id)
    if recording.user != request.user: raise PermissionDenied()
    if request.method == 'POST':
        form = EditAudioForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get('revert'):
                shutil.copy(recording.content_backup.path, recording.content.path)
            path = recording.content.path
            if path.split('.')[-1] != 'wav':
                wave_path = convert_wav(path)
                os.remove(path)
                path = wave_path
                recording.content = path
                recording.save()
            if form.cleaned_data.get('add_pitch_adjust'):
                adjust_pitch(path, form.cleaned_data.get('pitch_adjust'))
            if form.cleaned_data.get('add_reverb'):
                new_path = os.path.join(settings.MEDIA_ROOT, get_file_path(recording, recording.content.name))
                add_reverb(path, new_path, form.cleaned_data.get('reverb'))
                recording.content = new_path
                recording.save()
                os.remove(path)
            if form.cleaned_data.get('compress'):
                new_path = os.path.join(settings.MEDIA_ROOT, get_file_path(recording, recording.content.name))
                compressor(path, new_path, form.cleaned_data.get('threshold_db'), form.cleaned_data.get('ratio'))
                recording.content = new_path
                recording.save()
                os.remove(path)
            if form.cleaned_data.get('highpass'):
                new_path = os.path.join(settings.MEDIA_ROOT, get_file_path(recording, recording.content.name))
                highpass_filter(path, new_path, form.cleaned_data.get('highpass_cutoff_hz'))
                recording.content = new_path
                recording.save()
                os.remove(path)
            if form.cleaned_data.get('lowpass'):
                new_path = os.path.join(settings.MEDIA_ROOT, get_file_path(recording, recording.content.name))
                lowpass_filter(path, new_path, form.cleaned_data.get('lowpass_cutoff_hz'))
                recording.content = new_path
                recording.save()
                os.remove(path)
            if form.cleaned_data.get('gain_db') and abs(form.cleaned_data.get('gain_db')) > 0:
                new_path = os.path.join(settings.MEDIA_ROOT, get_file_path(recording, recording.content.name))
                gain(path, new_path, form.cleaned_data.get('gain_db'))
                recording.content = new_path
                recording.save()
                os.remove(path)
            if form.cleaned_data.get('normalize'):
                audio = AudioSegment.from_file(path)
                effects.normalize(audio)
                audio.export(path, format='wav')
            path = os.path.join(settings.MEDIA_ROOT, get_file_path(recording, 'plot.png'))
            if not recording.plot:
                recording.plot = path
                recording.save()
            visualize(recording.content.path, recording.plot.path)
            return redirect(reverse('synthesizer:edit-audio', kwargs={'id': recording.id}))
    form = EditAudioForm()
    return render(request, 'synthesizer/edit_audio.html', {
        'title': 'Edit Audio',
        'recording': recording,
        'form': form,
    })
