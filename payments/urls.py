from django.urls import path
from . import views

app_name='payments'

urlpatterns = [
    path('subscribe/crypto/<str:username>/', views.subscribe_bitcoin, name='subscribe-bitcoin'),
    path('subscribe/<str:username>/crypto/thankyou/', views.subscribe_bitcoin_thankyou, name='subscribe-bitcoin-thankyou'),
    path('subscribe/<str:username>/', views.subscribe_card, name='subscribe-card'),
#    path('tip/<str:username>/<str:tip>/', views.tip_card, name='tip-card'),
    path('tip/<str:username>/<str:tip>/crypto/', views.tip_bitcoin, name='tip-bitcoin'),
    path('tip/<str:username>/crypto/thankyou/', views.tip_bitcoin_thankyou, name='tip-bitcoin-thankyou'),
    path('crypto/<str:username>/', views.tip_crypto_simple, name='tip-crypto-simple'),
#    path('cancel/<str:username>/', views.cancel_subscription, name='cancel'),
#    path('cards/', views.card_list, name='cards'),
#    path('card/<int:id>/', views.card_primary, name='card'),
#    path('card/<int:id>/delete/', views.card_delete, name='delete'),
    path('photo/<str:username>/', views.buy_photo_card, name='buy-photo-card'),
    path('photo/<str:username>/crypto/', views.buy_photo_crypto, name='buy-photo-crypto'),
    path('audiovisual/checkout/', views.onetime_checkout_photo, name='photo-checkout'),
#    path('charge/', views.charge_card, name='charge-card'),
    path('checkout/monthly/', views.monthly_checkout_profile, name='monthly-checkout-profile'),
    path('cancel/<str:username>/', views.subscription_cancel, name='cancel-sub'),
    path('idscan/', views.idscan, name='idscan'),
    path('idscan/monthly/', views.monthly_checkout, name='monthly-checkout'),
    path('idscan/cancel/', views.subscription_cancel, name='cancel-subscription'),
    path('webdev/cancel/', views.webdev_subscription_cancel, name='cancel-webdev-subscription'),
    path('webdev/', views.webdev, name='webdev'),
    path('webdev/checkout/', views.onetime_checkout, name='webdev-checkout'),
    path('surrogacy/<str:username>/', views.surrogacy_info, name='surrogacy'),
    path('surrogacy/checkout/finalize/payment/', views.onetime_checkout_surrogacy, name='checkout-surrogacy'),
    path('surrogacy/checkout/<str:username>/', views.surrogacy, name='surrogacy-checkout'),
    path('cancel/', views.cancel, name='cancel'),
    path('success/', views.success, name='success'),
    path('webhook/', views.webhook, name='webhook'),
    path('connect/', views.connect_account, name='create-link'),
]
