from django.urls import path
from . import views

app_name='app'

urlpatterns = [
    path('', views.app, name='/'),
    path('', views.app, name='app'),
]