from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name='users'

from .views import (
    UserDeleteView,
)

urlpatterns = [
    path('all/', views.users, name='all'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_visitor, name='logout'),
    path('tfa/<str:username>/<str:usertoken>/', views.tfa, name='tfa'),
    path('tfa/onboarding/', views.tfa_onboarding, name='tfa_onboarding'),
    path('login/passwordless/', views.passwordless_login, name='passwordless'),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='users/password_reset.html',
             html_email_template_name='users/password_reset_html_email.html'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    path('resend_activation/', views.resend_activation, name='resend_activation'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('verify/', views.verify, name='verify'),
    path('unsubscribe/<str:username>/<token>/', views.unsubscribe, name='unsubscribe'),
    path('profile/', views.profile, name='profile'),
    path('user/<int:pk>/delete/', UserDeleteView.as_view(template_name='blog/user_confirm_delete.html'), name='delete-user'),
    path('user/<int:pk>/active/', views.toggle_user_active, name='toggle-user-active'),
    path('auth/google/', views.google_auth, name='youtube'),
    path('auth/callback/', views.google_auth_callback, name='oauth'),
]
