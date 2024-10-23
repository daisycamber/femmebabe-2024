from .models import Show
from django.utils import timezone

def is_live_show(request, model):
    show = Show.objects.filter(start__gte=timezone.now(), end__lte=timezone.now()).first()
    if show and not (show.model == request.user or show.user == request.user): return True
    return False

def get_live_show(request, model):
    show = Show.objects.filter(start__gte=timezone.now(), end__lte=timezone.now()).first()
    if show and not (show.model == request.user or show.user == request.user):
        return False
    return show
