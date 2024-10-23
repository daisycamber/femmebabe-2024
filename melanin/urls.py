from django.urls import path
from . import views

app_name='melanin'

urlpatterns = [
    path('', views.melanin, name='melanin'),
]