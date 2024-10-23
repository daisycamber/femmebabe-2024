from django.urls import path
from . import views

app_name='recordings'

urlpatterns = [
    path('profile/<str:username>/', views.recordings, name='recordings'),
    path('profile/<str:username>/idle/', views.recording_idle, name='recording_idle'),
    path('<str:uuid>/', views.recording, name='recording'),
    path('<str:uuid>/<int:index>/', views.recording_frame, name='recording-frame'),
    path('<int:pk>/delete/', views.RecordingDeleteView.as_view(template_name='recordings/recording_confirm_delete.html'), name='recording-delete'),
]
