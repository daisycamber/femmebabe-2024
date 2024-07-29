from django.urls import path
from . import views

app_name='security'

urlpatterns = [
    path('logout/all/', views.logout_everyone, name='logout-everyone'),
    path('logout/all/user/', views.logout_everyone_but_user, name='logout-everyone-but-user'),
    path('mrz/', views.scan_mrz, name='mrz'),
    path('nfc/', views.scan_nfc, name='nfc'),
    path('pin/', views.pincode, name='pin'),
    path('pin/set/', views.set_pincode, name='set-pin'),
    path('biometric/', views.webauth_redirect, name='biometric'),
    path('biometric/begin/', views.webauth_begin, name='begin-biometric'),
    path('modal/', views.modal, name='modal'),
    path('shake/', views.shake, name='shake'),
    path('logins/', views.logins, name='logins'),
    path('logins/<int:id>/approve/', views.approve_login, name='approve')
]
