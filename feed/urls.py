from django.urls import path

from .views import (
    PostUpdateView,
    PostDeleteView,
)
from . import views

app_name='feed'

urlpatterns = [
    path('home/', views.home, name='home'),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('private/<str:username>/', views.private, name='private'),
    path('grid/<str:username>/', views.profile_grid, name='profile-grid'),
    path('grid/api/<int:index>/', views.grid_api, name='grid-api'),
    path('follow/<str:username>/', views.follow, name='follow'),
    path('tip/<str:username>/<str:tip>/', views.tip, name='tip'),
#    path('unfollow/<str:username>/', views.unfollow, name='unfollow'),
    path('models/', views.profiles, name='profiles'),
    path('all/', views.all, name='all'),
    path('post/new/', views.new_post, name='new_post'),
    path('post/new/confirm/<str:id>/', views.new_post_confirm, name='new_post_confirm'),
    path('post/<str:uuid>/', views.post_detail, name='post-detail'),
    path('post/<int:pk>/publish/', views.publish, name='publish'),
    path('post/<int:pk>/pin/', views.pin, name='pin'),
    path('post/<str:uuid>/like/', views.like, name='like'),
    path('report/<str:uid>/', views.report, name='report'),
    path('post/<str:id>/bid/', views.auction, name='auction'),
    path('rotate/<int:pk>/<str:direction>/', views.rotate, name='rotate'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(template_name='feed/post_edit_form.html'), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('secure/photo/<str:filename>', views.secure_photo, name='secure-photo'),
    path('secure/video/<str:filename>', views.secure_video, name='secure-video'),
]
