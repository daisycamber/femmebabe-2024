from django.urls import path
from . import views

app_name='photobooth'

urlpatterns = [
    path('', views.photobooth, name='photobooth'),
    path('remote/', views.remote, name='remote'),
    path('photo/<str:camera>/', views.photo, name='photo'),
]