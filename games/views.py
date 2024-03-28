from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from feed.models import Post
from games.models import Game
from django.utils import timezone
import datetime
from django.contrib import messages
from .forms import JoinForm
import random

def invite(request, id):
    post = get_object_or_404(Post, uuid=id)
    code = str(random.randint(1111, 9999))
    user_code = str(random.randint(1111, 9999))
    while not (Game.objects.filter(uid=user_code, time__gte=timezone.now() - datetime.timedelta(hours=48)).last() or Game.objects.filter(uid=user_code, time__gte=timezone.now() - datetime.timedelta(hours=48)).last()):
        code = str(random.randint(1111, 9999))
        user_code = str(random.randint(1111, 9999))
    game = Game.objects.create(post=post, uid=user_code, code=code)
    return render(request, 'games/invite.html', {'game': game, 'code': code, 'user_code': user_code, 'post': post, 'title': 'Invite Player'})

def join(request):
    if request.method == 'POST':
        form = JoinForm(request.POST)
        if form.is_valid():
            game = Game.objects.filter(code=form.cleaned_data.get('code', None), time__gte=timezone.now() - datetime.timedelta(hours=48)).last()
            if not game:
                messages.warning(request, 'This code was not recognized. Please try again.')
                return redirect(request.path)
            game.started = True
            game.save()
            return redirect(reverse('games:play', kwargs={'id': game.uid, 'code': game.code}))
    return render(request, 'games/join.html', {'title': 'Join Game', 'form': JoinForm()})

def play(request, id, code):
    post = get_object_or_404(Post, uuid=id)
    game = Game.objects.filter(post=post, code=code, time__gte=timezone.now() - datetime.timedelta(hours=48)).last()
    player = False
    if not game:
        game = Game.objects.filter(post=post, uid=code, time__gte=timezone.now() - datetime.timedelta(hours=48)).last()
        player = True
    return render(request, 'games/game.html', {'hidenavbar': True, 'title': 'Play Game', 'post': post, 'game': game})
