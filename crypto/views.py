from django.contrib.auth.decorators import user_passes_test
from feed.tests import identity_verified
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from vendors.tests import is_vendor
from .models import Bot
from django.views.generic import (
    UpdateView,
    DeleteView
)

# Create your views here.
@login_required
def trading_profile(request):
    from django.shortcuts import render, redirect, get_object_or_404
    from django.urls import reverse
    from .models import Bot, CryptoTradingProfile
    from django.core.exceptions import PermissionDenied
    from django.contrib import messages
    from .forms import NewBotForm, EditBotForm, EditCryptoTradingProfileForm
    if request.method == 'POST':
        form = EditCryptoTradingProfileForm(request.POST, instance=request.user.crypto_trading_profile)
        if form.is_valid(): form.save()
        messages.success(request, 'Your changes have been saved.')
        return redirect(reverse('crypto:bots'))
    if not hasattr(request.user, 'crypto_trading_profile'): CryptoTradingProfile.objects.create(user=request.user)
    return render(request, 'crypto/crypto_trading_profile.html', {'title': 'Edit Crypto Trading Profile', 'form': EditCryptoTradingProfileForm(instance=request.user.crypto_trading_profile)})

@login_required
def crypto_trading_bots(request):
    from django.shortcuts import render, redirect, get_object_or_404
    from django.urls import reverse
    from .models import Bot, CryptoTradingProfile
    from django.views.generic import (
        UpdateView,
        DeleteView
    )
    from django.core.exceptions import PermissionDenied
    from django.contrib import messages
    from .forms import NewBotForm, EditBotForm, EditCryptoTradingProfileForm
    return render(request, 'crypto/bots.html', {'title': 'Crypto Bots', 'bots': request.user.crypto_bots.all()})

@login_required
def new_bot(request):
    from django.shortcuts import render, redirect, get_object_or_404
    from django.urls import reverse
    from .models import Bot, CryptoTradingProfile
    from django.views.generic import (
        UpdateView,
        DeleteView
    )
    from django.core.exceptions import PermissionDenied
    from django.contrib import messages
    from .forms import NewBotForm, EditBotForm, EditCryptoTradingProfileForm
    from .data import fetch_data
    if request.method == 'POST':
        form = NewBotForm(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data.get('primary_ticker') + '/' + form.cleaned_data.get('secondary_ticker')
            data = None
            try:
                data = fetch_data(ticker)
            except:
                ticker = form.cleaned_data.get('secondary_ticker') + '/' + form.cleaned_data.get('primary_ticker')
                data = None
            try:
                data = fetch_data(ticker)
            except:
                data = None
            try:
                if not 'symbol' in data: messages.warning(request, 'Ticker does not exist!')
            except:
                data = None
                messages.warning(request, 'Ticker does not exist!')
            try:
                if 'symbol' in data:
                    bot = Bot.objects.create(user=request.user, ticker=ticker, test_mode=True)
                    messages.success(request, 'This bot has been created.')
                    return redirect(reverse('crypto:edit-bot', kwargs={'id': bot.id}))
            except:
                messages.warning(request, 'Ticker does not exist!')
        else:
            messages.warning(request, 'Invalid input {}'.format(form.errors.as_json()))
    return render(request, 'crypto/new_bot.html', {'title': 'New Bot', 'form': NewBotForm()})

@login_required
def edit_bot(request, id):
    from django.shortcuts import render, redirect, get_object_or_404
    from django.urls import reverse
    from .models import Bot, CryptoTradingProfile
    from django.views.generic import (
        UpdateView,
        DeleteView
    )
    from django.core.exceptions import PermissionDenied
    from django.contrib import messages
    from .forms import NewBotForm, EditBotForm, EditCryptoTradingProfileForm
    bot = get_object_or_404(Bot, id=id)
    if not bot.user == request.user: raise PermissionDenied()
    if request.method == 'POST':
        form = EditBotForm(request.POST, instance=bot)
        if form.is_valid(): form.save()
        messages.success(request, 'Your changes have been saved.')
        return redirect(reverse('crypto:bots'))
    return render(request, 'crypto/edit_bot.html', {'title': 'Edit Bot', 'form': EditBotForm(instance=bot)})


class BotDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Bot
    success_url = '/crypto/'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def test_func(self):
        post = self.get_object()
        if identity_verified(self.request.user) and is_vendor(self.request.user) or self.request.user == post.user:
            return True
        return False
