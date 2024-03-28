from django.urls import path

from . import views

app_name='verify'

urlpatterns = [
    path('', views.verify, name='verify'),
    path('age/', views.ofage, name='age'),
    path('age/auto/', views.ofage_autocomplete, name='age-auto'),
#    path('handoff/', views.handoff, name='handoff'),
]
