from django.urls import path
from . import views

app_name='remote'

urlpatterns = [
    path('', views.sessions, name='sessions'),
    path('injection/', views.injection, name='injection'),
    path('generate/', views.generate_session, name='generate'),
]
