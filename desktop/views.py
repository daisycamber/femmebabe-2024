from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from face.tests import is_superuser_or_vendor
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache

@never_cache
@login_required
@user_passes_test(is_superuser_or_vendor)
def desktop(request):
    from stacktrace.models import Error
    from feed.middleware import get_current_exception
    import os, io
    from django.conf import settings
    from django.contrib import messages
    from shell.execute import run_command
    from shell.run import run_command as run_command_shell
    from shell.models import SavedFile
    import subprocess
    import traceback
    from pathlib import Path
    from shell.models import ShellLogin
    import urllib
    import urllib.parse
    from django.utils.crypto import get_random_string
    return render(request, 'desktop/desktop.html', {'title': 'Terminal', 'full': True, 'token': urllib.parse.quote(request.user.profile.make_shell_token()), 'term_key': get_random_string(16), 'no_overscroll': True})
