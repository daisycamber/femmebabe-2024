from django.contrib import admin
from .models import UserIpAddress
# Register your models here.
admin.site.register(UserIpAddress)
admin.site.register(UserIpAddress.history.model)
