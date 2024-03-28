from django.test import TestCase

# Create your tests here.

def is_superuser_or_vendor(user):
    if user.is_superuser or (hasattr(user, 'profile') and user.profile.admin):
        return True
    return False

