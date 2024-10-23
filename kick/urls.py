from django.urls import path
from . import views

app_name='kick'

urlpatterns = [
    path('', views.should_kick, name='should'),
    path('reasess/', views.reasess_kick, name='reasess'),
]
