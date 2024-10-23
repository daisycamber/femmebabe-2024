from django.urls import path
from . import views

app_name='face'

urlpatterns = [
    path('<str:username>/<str:token>/', views.face_verify, name='face'),
    path('auth/<str:username>/<str:token>/', views.auth_url, name='auth'),
    path('faces/', views.all_faces, name='faces'),
    path('secure/photo/<str:filename>', views.secure_photo, name='single-face')
]

