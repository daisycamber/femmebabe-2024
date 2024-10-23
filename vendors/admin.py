from django.contrib import admin
from .models import VendorProfile
# Register your models here.
admin.site.register(VendorProfile)
admin.site.register(VendorProfile.history.model)
