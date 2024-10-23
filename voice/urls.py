from django.urls import path
from . import views

app_name='voice'

urlpatterns = [
    path('', views.voice, name='voice'),
    path('recordings/', views.recordings, name='recordings'),
    path('option/add/', views.option_add, name='option-add'),
    path('recording/<str:id>/', views.recording, name='recording'),
    path('calls/', views.call_recordings, name='call-recordings'),
]
