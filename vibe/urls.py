from django.urls import path

from . import views

app_name='vibe'

urlpatterns = [
    path('', views.vibe, name='vibe'),
    path('remote/', views.remote_vibe, name='remote'),
    path('<str:username>/', views.receive_vibe, name='with'),
    path('setting/<str:username>/', views.recieve_vibe_setting, name='setting'),
]
