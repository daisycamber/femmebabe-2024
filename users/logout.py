from django.contrib.sessions.models import Session
from django.contrib.auth.models import User

def logout_all():
    for user in User.objects.all():
        logout_user(user)

def logout_user(user):
    from security.views import delete_all_unexpired_sessions_for_user
    delete_all_unexpired_sessions_for_user(user)
