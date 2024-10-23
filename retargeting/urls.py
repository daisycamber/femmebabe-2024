from django.urls import path
from . import views

app_name='retargeting'

urlpatterns = [
    path('email/', views.send_email, name='email'),
    path('emails/', views.emails, name='emails'),
    path('qrcode/', views.qrcode, name='qrcode')
]
