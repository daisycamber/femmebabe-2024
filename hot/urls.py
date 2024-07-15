from django.urls import path
from . import views

app_name='go'

urlpatterns = [
    path('', views.go, name='go'),
]
