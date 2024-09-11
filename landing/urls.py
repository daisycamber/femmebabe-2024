from django.urls import path
from . import views

app_name='landing'

urlpatterns = [
    path('about/', views.landing, name='landing'),
#    path('/', views.landing, name='/'),
    path('landing/', views.index, name='index'),
]
