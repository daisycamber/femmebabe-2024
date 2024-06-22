from django.urls import path
from . import views

app_name='crypto'

urlpatterns = [
    path('', views.crypto_trading_bots, name='bots'),
    path('new/', views.new_bot, name='new-bot'),
    path('profile/', views.trading_profile, name='profile'),
    path('edit/<int:id>/', views.edit_bot, name='edit-bot'),
    path('delete/<int:pk>/', views.BotDeleteView.as_view(template_name='crypto/delete_bot.html'), name='delete-bot'),
]
