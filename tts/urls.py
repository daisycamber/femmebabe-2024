from django.urls import path
from . import views

app_name='tts'

urlpatterns = [
    path('<str:word>/', views.word, name='word'),
]
