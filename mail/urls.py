from django.urls import path
from . import views

app_name='mail'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('message/<str:id>/', views.message, name='message'),
]
