from django.shortcuts import render
from django.conf import settings
from django.views.decorators.cache import cache_control

# Create your views here.
@cache_control(public=True)
def app(request):
    return render(request, 'app/app.html', {'title': 'App', 'hidenavbar': True, 'full': True, 'nopadding': True, 'default_page': settings.DEFAULT_PAGE})
