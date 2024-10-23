from django.urls import path
from . import views

app_name='notifications'

urlpatterns = [
    path('', views.send_guest_notification, name='send'),
]