from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from face.tests import is_superuser_or_vendor
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache

@never_cache
@login_required
@user_passes_test(is_superuser_or_vendor)
def terminal(request):
    from django.shortcuts import render, redirect, get_object_or_404
    from django.http import HttpResponse
    from stacktrace.models import Error
    from feed.middleware import get_current_exception
    from .forms import CommandForm, EditFileForm
    from .execute import run_command
    from .reload import safe_reload
    from .tests import is_admin
    import os, io
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
    import urllib
    from django.utils.crypto import get_random_string
    return render(request, 'shell/terminal.html', {'title': 'Terminal', 'full': True, 'token': urllib.parse.quote(request.user.profile.make_shell_token()), 'term_key': get_random_string(16), 'no_overscroll': True})

@csrf_exempt
@login_required
@user_passes_test(is_superuser_or_vendor)
def approve_login(request, id):
    from django.shortcuts import render, redirect, get_object_or_404
    from django.http import HttpResponse
    from stacktrace.models import Error
    from feed.middleware import get_current_exception
    from .forms import CommandForm, EditFileForm
    from .execute import run_command
    from .reload import safe_reload
    from .tests import is_admin
    import os, io
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
    login = ShellLogin.objects.filter(id=id).first()
    if request.method == 'POST' and login:
        login.approved = True
        login.validated = True
        login.save()
    return HttpResponse('<i class="bi bi-door-open-fill"></i>')

@csrf_exempt
@login_required
@user_passes_test(is_superuser_or_vendor)
def invalidate_login(request, id):
    from django.shortcuts import render, redirect, get_object_or_404
    from django.http import HttpResponse
    from stacktrace.models import Error
    from feed.middleware import get_current_exception
    from .forms import CommandForm, EditFileForm
    from .execute import run_command
    from .reload import safe_reload
    from .tests import is_admin
    import os, io
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
    login = ShellLogin.objects.filter(id=id).first()
    if request.method == 'POST' and login:
        login.approved = False
        login.validated = True
        login.save()
    return HttpResponse('<i class="bi bi-door-closed-fill"></i>')

@login_required
@user_passes_test(is_superuser_or_vendor)
def logins(request):
    from django.shortcuts import render, redirect, get_object_or_404
    from django.http import HttpResponse
    from stacktrace.models import Error
    from feed.middleware import get_current_exception
    from .forms import CommandForm, EditFileForm
    from .execute import run_command
    from .reload import safe_reload
    from .tests import is_admin
    import os, io
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
    the_logins = ShellLogin.objects.filter(approved=False, validated=False).order_by('-time')
    return render(request, 'shell/logins.html', {
        'title': 'Approve Logins',
        'logins': list(the_logins)[:32]
    })

@login_required
@user_passes_test(is_superuser_or_vendor)
def read(request, id):
    from django.shortcuts import render, redirect, get_object_or_404
    from django.http import HttpResponse
    from stacktrace.models import Error
    from feed.middleware import get_current_exception
    from .forms import CommandForm, EditFileForm
    from .execute import run_command
    from .reload import safe_reload
    from .tests import is_admin
    import os, io
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
    content = ''
    try:
        file = SavedFile.objects.get(id=id)
        content = file.content
    except: pass
    return HttpResponse(content)

@login_required
@user_passes_test(is_superuser_or_vendor)
def reload(request):
    from django.shortcuts import render, redirect, get_object_or_404
    from django.http import HttpResponse
    from stacktrace.models import Error
    from feed.middleware import get_current_exception
    from .forms import CommandForm, EditFileForm
    from .execute import run_command
    from .reload import safe_reload
    from .tests import is_admin
    import os, io
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
    if request.method == 'POST':
        safe_reload()
    return HttpResponse(200)

@login_required
@user_passes_test(is_superuser_or_vendor)
def edit(request):
    from django.shortcuts import render, redirect, get_object_or_404
    from django.http import HttpResponse
    from stacktrace.models import Error
    from feed.middleware import get_current_exception
    from .forms import CommandForm, EditFileForm
    from .execute import run_command
    from .reload import safe_reload
    from .tests import is_admin
    import os, io
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
    path = os.path.join(settings.BASE_DIR, request.GET.get('path'))
    if request.method == 'POST':
        form = EditFileForm(request.POST)
        if form.is_valid() and not path.startswith('/etc/sudoers'):
#            if not form.cleaned_data.get('length') == len(form.cleaned_data.get('text')): return HttpResponse('Incomplete input')
            from lotteh.celery import update_file
            update_file.delay(path, form.cleaned_data.get('text'), request.user.id)
            return HttpResponse('Saved.')
    content = ''
    if not os.path.exists(path): content = ''
    else:
        with io.open(path, "r", encoding="utf-8") as f:
            content = str(f.read())
    return render(request, 'shell/edit.html', {'title': 'Edit file', 'pagetitle': 'Edit file', 'trace': '', 'full': True, 'form': EditFileForm(initial={'text': content}), 'saved_files': SavedFile.objects.filter(path=str(path), current=False).order_by('-saved_at')})
@never_cache
@login_required
@user_passes_test(is_superuser_or_vendor)
def shell(request):
    from django.shortcuts import render, redirect, get_object_or_404
    from django.http import HttpResponse
    from stacktrace.models import Error
    from feed.middleware import get_current_exception
    from .forms import CommandForm, EditFileForm
    from .execute import run_command
    from .reload import safe_reload
    from .tests import is_admin
    import os, io
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
    import urllib
    if request.method == 'POST':
        from errors.highlight import highlight_code, highlight_shell
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
            output = '<iframe src="/shell/edit/?hidenavbar=t&path=' + file + '" width="100%;" height="590px;"></iframe>'
        elif command.split(' ')[0] == 'cancel':
            output = highlight_shell(run_command_shell("\x03"))
        else:
            try:
                output = highlight_shell(run_command_shell(command))
            except:
                output = highlight_code('invalid command.')
                print(traceback.format_exc())
        return HttpResponse('{}$ {}'.format(request.user.profile.preferred_name, command) + output)
    from django.utils.crypto import get_random_string
    return render(request, 'shell/shell.html', {'title': 'Shell', 'pagetitle': 'Shell', 'trace': '', 'full': True, 'form': CommandForm(), 'token': urllib.parse.quote(request.user.profile.make_shell_token()), 'term_key': get_random_string(16)})
