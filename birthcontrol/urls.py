from django.urls import path
from . import views

app_name='birthcontrol'

urlpatterns = [
    path('take/', views.take_birth_control, name='take'),
    path('take/time/', views.take_birth_control_time, name='take-time'),
    path('notes/', views.notes, name='notes'),
    path('profile/', views.profile, name='profile'),
    path('temperature/', views.temperature, name='temperature'),
]
