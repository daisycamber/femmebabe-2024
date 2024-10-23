from django.urls import path
from . import views

app_name='games'

urlpatterns = [
    path('', views.join, name='join'),
    path('<str:id>/', views.invite, name='invite'),
    path('<str:id>/<str:code>/', views.play, name='play'),
]
