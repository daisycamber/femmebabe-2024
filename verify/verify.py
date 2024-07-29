from django.db import models
from django.contrib.auth.models import User
import math
from PIL import Image
from django.utils import timezone
import os, traceback
from feed.blur import blur_faces
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.urls import reverse
from django.utils.html import strip_tags
from django.db.models import CharField
from django.db.models.functions import Length
import shutil
from django.utils.crypto import get_random_string
from django.conf import settings
from security.secure import get_secure_path, get_secure_public_path
from feed.apis import is_safe_public_image
from verify.validation import verify_id_document
from verify.forensics import text_matches_name, text_matches_birthday
from verify.ocr import get_image_text
from datetime import date
import sys, pytz
from feed.align import face_angle_detect
from verify.barcode import barcode_valid
import uuid
import os
from barcode.idscantext import decode_ocr

def get_uuid():
    id = "%s" % (uuid.uuid4())
    return id

import random

def validate_id(verification):
    verification.save()
    self = verification
    id_path = verification.document.path
    faces = verification.user.faces.all()
    try:
        birthday, expiry = barcode_valid(verification)
        if not birthday:
            return False
        verification.birthdate = birthday
        if expiry:
            verification.expiry = expiry
        verification.save()
    except:
        return False
    if not birthday:
        return False
    if not verification.user.profile.disable_id_face_match and (id_path == None or faces.count() == 0):
        return False
    if not verification.user.profile.disable_id_face_match and not verify_id_document(id_path, faces):
        print("Failed to verify document due to face mismatch.")
        return False
    no_lang = get_image_text(id_path, lang=None)
    verification.document_ocr = get_image_text(id_path, lang='eng')
    if len(no_lang) > len(verification.document_ocr): verification.document_ocr = no_lang
    verification.save()
    name = verification.full_name
    if not text_matches_name(verification.document_ocr, name):
        return False
    if not text_matches_birthday(verification.document_ocr, verification.birthday.strftime('%m/%d/%Y')):
        return False
    if not verification.document_number in verification.document_ocr:
        return False
    if len(verification.document_ocr) < 100:
        return False
    if len(verification.barcode_data) < 200:
        return False
    today = date.today()
    age = today.year - verification.birthday.year - ((today.month, today.day) < (verification.birthday.month, verification.birthday.day))
    if age < settings.MIN_AGE_VERIFIED:
        return False
    if settings.USE_IDWARE and not decode_ocr(verification.barcode_data, verification):
        print('IDScan API failed.')
        return False
#    return text_has_valid_birthday_and_expiry(verification.document_ocr):
    verification.verified = True
    verification.save()
    return True
