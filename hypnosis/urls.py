from django.urls import path
from . import views

app_name='hypnosis'

urlpatterns = [
    path('', views.hypnosis, name='hypnosis'),
]
