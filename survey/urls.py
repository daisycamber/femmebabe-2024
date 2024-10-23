from django.urls import path
from . import views

app_name='survey'

urlpatterns = [
    path('', views.answer, name='answer'),
    path('list/', views.surveys, name='surveys'),
    path('completed/', views.has_completed_survey, name='completed'),
    path('update/<str:id>/', views.update, name='update'),
    path('answer/<int:id>/', views.survey, name='survey'),
]
