import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lotteh.settings')

import django
django.setup()

OLDPROJ = 'lotteh'
NEWPROJ = 'lotteh'
OLDUSER = 'team'
NEWUSER = 'team'

from feed.models import Post
from users.models import Profile
from birthcontrol.models import BirthControlProfile
from barcode.models import DocumentScan
from voice.models import AudioInteractive

for post in Post.objects.all():
    if post.image:
        post.image = str(post.image.path).replace(OLDPROJ, NEWPROJ).replace(OLDUSER, NEWUSER)
        try:
            post.save()
        except: pass
    if post.image_original:
        post.image_original = str(post.image_original.path).replace(OLDPROJ, NEWPROJ).replace(OLDUSER, NEWUSER)
        try:
            post.save()
        except: pass
    if post.file:
        post.file = str(post.file.path).replace(OLDPROJ, NEWPROJ).replace(OLDUSER, NEWUSER)
        try:
            post.save()
        except: pass

for post in Profile.objects.all():
    if post.image:
        post.image = str(post.image.path).replace(OLDPROJ, NEWPROJ).replace(OLDUSER, NEWUSER)
        try:
            post.save()
        except: pass
    if post.image_public:
        post.image_public = str(post.image_public.path).replace(OLDPROJ, NEWPROJ).replace(OLDUSER, NEWUSER)
        try:
            post.save()
        except: pass
    if post.cover_image:
        post.cover_image = str(post.cover_image.path).replace(OLDPROJ, NEWPROJ).replace(OLDUSER, NEWUSER)
        try:
            post.save()
        except: pass

for post in BirthControlProfile.objects.all():
    if post.birth_control:
        post.birth_control = str(post.birth_control.path).replace(OLDPROJ, NEWPROJ).replace(OLDUSER, NEWUSER)
        try:
            post.save()
        except: pass
    if post.birth_control_current:
        post.birth_control_current = str(post.birth_control_current.path).replace(OLDPROJ, NEWPROJ).replace(OLDUSER, NEWUSER)
        try:
            post.save()
        except: pass

for post in DocumentScan.objects.all():
    if post.document:
        post.document = str(post.document.path).replace(OLDPROJ, NEWPROJ).replace(OLDUSER, NEWUSER)
        try:
            post.save()
        except: pass
    if post.document_full:
        post.document_full = str(post.document_full.path).replace(OLDPROJ, NEWPROJ).replace(OLDUSER, NEWUSER)
        try:
            post.save()
        except: pass
    if post.document_isolated:
        post.document_isolated = str(post.document_isolated.path).replace(OLDPROJ, NEWPROJ).replace(OLDUSER, NEWUSER)
        try:
            post.save()
        except: pass

for post in AudioInteractive.objects.all():
    if post.content:
        post.content = str(post.content.path).replace(OLDPROJ, NEWPROJ).replace(OLDUSER, NEWUSER)
        try:
            post.save()
        except: pass
