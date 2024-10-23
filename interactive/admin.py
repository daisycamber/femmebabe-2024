from django.contrib import admin
from .models import Choice, Choices, UserChoice

# Register your models here.

admin.site.register(Choice)
admin.site.register(UserChoice)
admin.site.register(Choices)
