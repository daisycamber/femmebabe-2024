"""lotteh URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from users import views as user_views
from kick import views as kick_views
from landing import views as landing_views
from errors import views as error_views
from misc import views as misc_views
from django_summernote.urls import urlpatterns as summernote_urlpatterns
from django.conf import settings

urlpatterns = [
    path('', include(('app.urls'), namespace='app')),
    path('', include(('landing.urls'), namespace='landing')),
    path('', include(('misc.urls'), namespace='misc')),
    path('logs/', error_views.logs, name='logs'),
    path('logs/api/', error_views.logs_api, name='logs-api'),
    path('admin/login/', user_views.login),
    path('admin/', admin.site.urls),
    path('', landing_views.landing, name='/'),
    path('accounts/', include(('users.urls'), namespace='users')),
    path('feed/', include(('feed.urls'), namespace='feed')),
    path('vendors/', include(('vendors.urls'), namespace='vendors')),
    path('vibe/', include(('vibe.urls'), namespace='vibe')),
    path('live/', include(('live.urls'), namespace='live')),
    path('chat/', include(('chat.urls'), namespace='chat')),
    path('verify/', include(('verify.urls'), namespace='verify')),
    path('birthcontrol/', include(('birthcontrol.urls'), namespace='birthcontrol')),
    path('go/', include(('go.urls'), namespace='go')),
    path('security/', include(('security.urls'), namespace='security')),
    path('recordings/', include(('recordings.urls'), namespace='recordings')),
    path('interactive/', include(('interactive.urls'), namespace='interactive')),
    path('voice/', include(('voice.urls'), namespace='voice')),
    path('sms/', include(('sms.urls'), namespace='sms')),
    path('face/', include(('face.urls'), namespace='face')),
    path('kick/', include(('kick.urls'), namespace='kick')),
    path('audio/', include(('audio.urls'), namespace='audio')),
    path('tts/', include(('tts.urls'), namespace='tts')),
    path('payments/', include(('payments.urls'), namespace='payments')),
    path('recovery/', include(('recovery.urls'), namespace='recovery')),
    path('barcode/', include(('barcode.urls'), namespace='barcode')),
    path('shell/', include(('shell.urls'), namespace='shell')),
    path('hypnosis/', include(('hypnosis.urls'), namespace='hypnosis')),
    path('photobooth/', include(('photobooth.urls'), namespace='photobooth')),
    path('notifications/', include(('notifications.urls'), namespace='notifications')),
    path('survey/', include(('survey.urls'), namespace='survey')),
    path('synthesizer/', include(('synthesizer.urls'), namespace='synthesizer')),
    path('crypto/', include(('crypto.urls'), namespace='crypto')),
    path('melanin/', include(('melanin.urls'), namespace='melanin')),
    path('remote/', include(('remote.urls'), namespace='remote')),
    path('send/', include(('retargeting.urls'), namespace='retargeting')),
    path('mail/', include(('mail.urls'), namespace='mail')),
    path('contact/', include(('contact.urls'), namespace='contact')),
    path('meet/', include(('meet.urls'), namespace='meet')),
    path('games/', include(('games.urls'), namespace='games')),
    path('desktop/', include(('desktop.urls'), namespace='desktop')),
    path('appeal/', kick_views.reasess_kick, name='appeal'),
    path('password-reset-confirm/<uidb64>/<token>/', user_views.password_reset, name='password_reset_confirm'),
#         auth_views.PasswordResetConfirmView.as_view(
#             template_name='users/password_reset_confirm.html'
#         ),
#         name='password_reset_confirm'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    path('', include('pwa_webpush.urls')),
    path('summernote/', include('django_summernote.urls')),
#    path('webpush/', include('webpush.urls'))
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('allauth.socialaccount.urls')),
    path("__debug__/", include("debug_toolbar.urls")),
    path("webauth/", include("webauth.urls")),
]

handler404 = 'errors.views.handler404'
handler500 = 'errors.views.handler500'
handler403 = 'errors.views.handler403'
handler400 = 'errors.views.handler400'

title = '{} Admin Panel'.format(settings.SITE_NAME)

admin.site.site_title = title
admin.site.site_title = title
admin.site.index_title = title
