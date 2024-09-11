from django.urls import path
from . import views

app_name='recovery'

urlpatterns = [
    path('<str:name>/', views.recovery, name='recovery'),
    path('secure/<str:token>/', views.user_recovery, name='secure'),
    path('', views.recover, name='recover'),
]
