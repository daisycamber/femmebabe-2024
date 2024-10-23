from django.urls import path

from . import views

app_name='chat'

urlpatterns = [
    path('', views.chat_self, name='chat_self'),
    path('video/', views.video, name='video'),
    path('video/mirror/', views.mirror, name='mirror'),
    path('<str>/video/', views.video_redirect, name='video-redirect'),
    path('<str:username>/', views.chat, name='chat'),
    path('raw/<str:username>/', views.raw, name='raw'),
    path('with/<str:username>/', views.has_message, name='has_message'),
    path('<int:pk>/delete/', views.ChatDeleteView.as_view(), name='delete'),
]
