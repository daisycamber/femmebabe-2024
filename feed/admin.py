from django.contrib import admin
from .models import Post, Report
from django.contrib.admin.models import LogEntry

# Register your models here.
admin.site.register(Post)
admin.site.register(Post.history.model)
admin.site.register(Report)
admin.site.register(LogEntry)
