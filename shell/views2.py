from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from stacktrace.models import Error
from feed.middleware import get_current_exception
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from face.tests import is_superuser_or_vendor
from django.views.decorators.csrf import csrf_exempt
from errors.highlight import highlight_code, highlight_shell
from .forms import CommandForm, EditFileForm
from .execute import run_command
from .reload import safe_reload
import os
from django.conf import settings
from django.http import Http404
from django.contrib import messages
from shell.execute import run_command
from shell.run import run_command as run_command_shell
from shell.models import SavedFile
import subprocess
import traceback
from pathlib import Path
from shell.models import ShellLogin

@csrf_exempt
@login_required
def approve_login(request, id):
    login = get_object_or_404(ShellLogin, id=id)
    if request.method == 'POST':
        login.approved = True
        login.save()
        return HttpResponse('<i class="bi bi-door-open-fill"></i>')

@login_required
@user_passes_test(is_superuser_or_vendor)
def logins(request):
    the_logins = ShellLogin.objects.filter(approved=False).order_by('-time')
    return render(request, 'shell/logins.html', {
        'title': 'Approve Logins',
        'logins': list(the_logins)[:32]
    })

@login_required
@user_passes_test(is_superuser_or_vendor)
def read(request, id):
    content = ''
    try:
        file = SavedFile.objects.get(id=id)
        content = file.content
    except: pass
    return HttpResponse(content)

@login_required
@user_passes_test(is_superuser_or_vendor)
def reload(request):
    if request.method == 'POST':
        safe_reload()
    return HttpResponse(200)

@login_required
@user_passes_test(is_superuser_or_vendor)
def edit(request):
    path = os.path.join(settings.BASE_DIR, request.GET.get('path'))
    if request.method == 'POST':
        form = EditFileForm(request.POST)
        if form.is_valid() and not path.startswith('/etc/sudoers'):
            new_text = form.cleaned_data.get('text')
            status = None
            owner = None
            group = None
            path_exists = os.path.exists(path)
            if path_exists:
                status = os.stat(path)
                path = Path(str(path))
                owner = path.owner()
                group = path.group()
                run_command('sudo chmod a+rw ' + str(path))
            with open(path, 'w') as f:
                f.writelines(new_text)
            if path_exists:
                run_command('sudo chmod a-rw ' + str(path))
                run_command('sudo chown {}:{}'.format(owner, group) + ' ' + str(path))
                run_command('sudo chmod ' + oct(status.st_mode)[-3:] + ' ' + str(path))
            for file in SavedFile.objects.filter(path=str(path), current=True):
                file.current = False
                file.save()
            file = SavedFile.objects.create(user=request.user, path=str(path), content=new_text, current=True)
            file.save()
            messages.success(request, 'This file has been updated.')
    content = ''
    if not os.path.exists(path): content = ''
    else:
        with open(path) as f:
            content = str(f.read())
    return render(request, 'shell/edit.html', {'title': 'Edit file', 'pagetitle': 'Edit file', 'trace': '', 'full': True, 'form': EditFileForm(initial={'text': content}), 'saved_files': SavedFile.objects.filter(path=str(path), current=False).order_by('-saved_at')})

login_required
@user_passes_test(is_superuser_or_vendor)
def shell(request):
    if request.method == 'POST':
        form = CommandForm(request.POST)
        command = ''
        if form.is_valid():
            command = form.cleaned_data.get('input')
        output = ''
        if len(command) == 0:
            output = highlight_code('empty command.')
        elif command == 'reload':
            output = highlight_code(safe_reload())
        elif command.split(' ')[0] == 'clear':
            output = '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n'
        elif command.split(' ')[0] == 'nano':
            file = command.split(' ')[1]
            output = '<iframe src="/shell/edit/?hidenavbar=t&path=' + file + '" width="100%;" height="560px;"></iframe>'
        elif command.split(' ')[0] == 'cancel':
            output = highlight_shell(run_command_shell("\x03"))
        else:
            try:
                output = highlight_shell(run_command_shell(command))
            except:
                output = highlight_code('invalid command.')
                print(traceback.format_exc())
        return HttpResponse('{}$ {}'.format(request.user.profile.name, command) + output)
    return render(request, 'shell/shell.html', {'title': 'Shell', 'pagetitle': 'Shell', 'trace': '', 'full': True, 'form': CommandForm()})