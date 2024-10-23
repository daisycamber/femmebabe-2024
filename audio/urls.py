
from django.urls import path
from . import views

app_name='audio'

urlpatterns = [
    path('', views.recordings, name='recordings'),
    path('<str:id>/', views.recording, name='record'),
    path('<str:id>/publish/', views.publish, name='publish'),
    path('confirm/<str:id>/', views.confirm, name='confirm'),
    path('<str:id>/post/', views.add_post, name='add-post'),
]
