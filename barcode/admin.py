from django.contrib import admin
from .models import DocumentScan

admin.site.register(DocumentScan)
admin.site.register(DocumentScan.history.model)
