from threading import local
import traceback
from django.utils.deprecation import MiddlewareMixin

_request = local()

_error = local()

class CurrentRequestMiddleware(MiddlewareMixin):
    def process_request(self, request):
        _request.value = request

def get_current_request():
    try:
        return _request.value
    except AttributeError:
        return None


class ExceptionVerboseMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        _error.value = traceback.format_exc()

def get_current_exception():
    try:
        return _error.value
    except AttributeError:
        return None

def set_current_exception(exception):
    try:
        _error.value = exception
    except AttributeError:
        print('Attribute error setting exception.')

_user = local()

class CurrentUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        _user.value = request.user


def get_current_user():
    try:
        return _user.value if _user.value.is_authenticated else None
    except AttributeError:
        return None