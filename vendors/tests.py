from django.test import TestCase

# Create your tests here.
def is_vendor(user):
    return user.profile.vendor
