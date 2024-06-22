from django.contrib import admin
from .models import Post
from django.contrib.admin.models import LogEntry

# Register your models here.
admin.site.register(Post)
admin.site.register(LogEntry)
