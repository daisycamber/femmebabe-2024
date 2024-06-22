from django.urls import path
from . import views

app_name='barcode'

urlpatterns = [
    path('', views.scan_barcode, name='scan'),
    path('validate/<str:key>/', views.validate_barcode, name='validate'),
]