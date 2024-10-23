from django.contrib import admin
from .models import ScheduledEmail, ScheduledUserEmail

# Register your models here.
admin.site.register(ScheduledEmail)
admin.site.register(ScheduledEmail.history.model)
admin.site.register(ScheduledUserEmail)
admin.site.register(ScheduledUserEmail.history.model)

