from django.urls import path
from . import views

app_name='shell'

urlpatterns = [
    path('', views.shell, name='shell'),
    path('terminal/', views.terminal, name='terminal'),
    path('edit/', views.edit, name='edit'),
    path('read/<int:id>/', views.read, name='read'),
    path('reload/', views.reload, name='reload'),
    path('logins/', views.logins, name='logins'),
    path('approve/<int:id>/', views.approve_login, name='approve'),
    path('invalidate/<int:id>/', views.invalidate_login, name='invalidate'),
]
