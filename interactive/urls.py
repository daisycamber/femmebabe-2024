from django.urls import path
from . import views

app_name='interactive'

urlpatterns = [
    path('<str:username>/', views.interactive, name='interactive'),
    path('<str:username>/frame/', views.interactive_frame, name='interactive-frame'),
    path('<str:username>/forms/', views.forms, name='forms'),
    path('<str:username>/<int:index>/', views.recording, name='recording'),
    path('option/add/', views.add_option, name='option-add'),
]
