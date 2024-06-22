from django.urls import path, re_path

app_name='live'

from . import views

urlpatterns = [
    path('go/', views.golivevideo, name='golivevideo'),
    path('confirm/<str:id>/', views.confirm, name='confirm'),
    path('camera/name/', views.name_camera, name='name-camera'),
    path('cameras/', views.choose_live_camera, name='choose-live-camera'),
    path('cameras/name/', views.choose_camera, name='choose-camera'),
    path('shows/', views.shows, name='shows'),
    path('remote/api/', views.remote_api, name='remote-api'),
    path('remote/', views.remote, name='remote'),
    path('mute/', views.mute, name='mute'),
    path('remote/record/', views.record_remote, name='record-remote'),
    path('video/<str:filename>', views.stream_secure_video, name='stream-secure-video'),
    path('video/fast/<str:filename>', views.stream_video, name='stream-video'),
    path('still/<str:filename>', views.still, name='still'),
    path('<str:username>/', views.livevideo, name='livevideo'),
    path('<str:username>/book/', views.book_show, name='book-live-show'),
    path('<str:username>/frame/', views.video_frame, name='framevideo'),
    path('<str:username>/frame/last/', views.last_frame_video, name='last-frame-video'),
]
