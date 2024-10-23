from django.contrib import admin
from .models import Profile
# Register your models here.
admin.site.register(Profile)
admin.site.register(Profile.history.model)
from simple_history import register
from django.contrib.auth.models import User
register(User)
