from django.urls import path
from . import views

app_name='synthesizer'

urlpatterns = [
    path('edit/<int:id>/', views.audio_recording, name='edit-audio'),
    path('project/<str:id>/', views.project, name='project'),
    path('projects/', views.projects, name='projects'),
]