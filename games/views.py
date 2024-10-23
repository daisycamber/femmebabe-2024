from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page

def get_num_length(num, length):
    n = ''
    for x in range(length):
        n = n + str(num)
    return int(n)

def invite(request, id):
    from django.urls import reverse
    from feed.models import Post
    from games.models import Game
    from django.utils import timezone
    import datetime
    import random
    from django.conf import settings
    from django.shortcuts import render, get_object_or_404, redirect
    post = get_object_or_404(Post, id=id)
    code = str(random.randint(get_num_length(1, settings.GAME_CODE_LENGTH), get_num_length(9, settings.GAME_CODE_LENGTH)))
    user_code = str(random.randint(get_num_length(1, settings.GAME_CODE_LENGTH), get_num_length(9, settings.GAME_CODE_LENGTH)))
    while (Game.objects.filter(uid=user_code, time__gte=timezone.now() - datetime.timedelta(hours=48)).last() or Game.objects.filter(uid=user_code, time__gte=timezone.now() - datetime.timedelta(hours=48)).last()):
        code = str(random.randint(get_num_length(1, settings.GAME_CODE_LENGTH), get_num_length(9, settings.GAME_CODE_LENGTH)))
        user_code = str(random.randint(get_num_length(1, settings.GAME_CODE_LENGTH), get_num_length(9, settings.GAME_CODE_LENGTH)))
    game = Game.objects.create(post=post, uid=user_code, code=code)
    return render(request, 'games/invite.html', {'game': game, 'code': code, 'user_code': user_code, 'post': post, 'title': 'Invite Player', 'small': True})

@csrf_exempt
@cache_page(60*60*24*30)
def join(request):
    from .forms import JoinForm
    from django.urls import reverse
    from games.models import Game
    from django.utils import timezone
    import datetime
#    from django.conf import settings
    from django.shortcuts import redirect
    if request.method == 'POST':
        form = JoinForm(request.POST)
        if form.is_valid():
            game = Game.objects.filter(code=form.cleaned_data.get('code', None), time__gte=timezone.now() - datetime.timedelta(hours=48)).last()
            if not game:
                messages.warning(request, 'This code was not recognized. Please try again.')
                return redirect(request.path)
            game.started = True
            game.save()
            return redirect(reverse('games:play', kwargs={'id': game.post.id, 'code': game.code}))
    from django.shortcuts import render
    return render(request, 'games/join.html', {'title': 'Join Game', 'form': JoinForm(), 'small': True})

def play(request, id, code):
    from .forms import JoinForm
    from django.urls import reverse
    from games.models import Game
    from django.utils import timezone
    import datetime
    from feed.models import Post
#    from django.conf import settings
    from django.shortcuts import render, get_object_or_404, redirect
    post = get_object_or_404(Post, id=id)
    game = Game.objects.filter(post=post, code=code, time__gte=timezone.now() - datetime.timedelta(hours=48)).last()
    player = False
    if not game:
        game = Game.objects.filter(post=post, uid=code, time__gte=timezone.now() - datetime.timedelta(hours=48)).last()
        player = True
    return render(request, 'games/game.html', {'hidenavbar': True, 'title': 'Play Game', 'post': post, 'game': game, 'player': player, 'full': True})
