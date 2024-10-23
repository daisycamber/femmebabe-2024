from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from face.tests import is_superuser_or_vendor
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
@login_required
@user_passes_test(is_superuser_or_vendor)
def logs(request):
    from django.shortcuts import render
    from errors.highlight import highlight_code
    from .logs import get_logs
    logs = highlight_code(get_logs())
    return render(request, 'errors/live_error.html', {'title': 'Error Logs', 'pagetitle': 'Error Logs', 'notes': 'These are the recent error logs.', 'trace': logs, 'full': True})

@login_required
@user_passes_test(is_superuser_or_vendor)
def logs_api(request):
    from django.http import HttpResponse
    from errors.highlight import highlight_code
    from .logs import get_logs
    logs = highlight_code(get_logs())
    return HttpResponse(logs)

def handler404(request, exception):
    from django.shortcuts import redirect
    if not request.path.endswith('/'): return redirect(request.path + '/')
    from django.shortcuts import render
    return render(request, 'errors/error.html', {'title': 'Error 404', 'pagetitle': 'Error 404', 'notes': 'This page was not found on the server. It may have moved or been deleted.', 'is_404': True})

def handler500(request):
    from feed.middleware import get_current_exception
    print(get_current_exception())
    user = None
    if hasattr(request, 'user') and request.user and request.user.is_authenticated:
        user = request.user
    try:
        from .models import Error
        Error.objects.create(user=user, stack_trace=get_current_exception(), notes='Logged by 500 handler.')
    except: pass
    from django.shortcuts import render
    return render(request, 'errors/error.html', {'title': 'Error 500', 'pagetitle': 'Error 500', 'notes': 'There is a problem with the server, or with a request coming from you. Thank you for your understanding while we get things set up.', 'trace': get_current_exception()})


def handler403(request, exception):
    from django.shortcuts import render
    return render(request, 'errors/error.html', {'title': 'Error 403', 'pagetitle': 'Error 403', 'notes': 'You don\'t have permission to preform this request. If you think this is in error, please contact the server administrator.', 'is_403': True})

def handler400(request, exception):
    from django.shortcuts import render
    return render(request, 'errors/error.html', {'title': 'Error 400', 'pagetitle': 'Error 400', 'notes': 'This was a bad request.'})
