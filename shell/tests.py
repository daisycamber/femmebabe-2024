from django.test import TestCase

# Create your tests here.
def is_admin(user):
    return user.profile.admin
