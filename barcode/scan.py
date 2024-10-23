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
import celery
from security.secure import get_secure_path, get_secure_public_path
from feed.apis import is_safe_public_image
from verify.validation import verify_id_document
from verify.forensics import text_matches_name, text_matches_birthday, text_has_valid_birthday_and_expiry
from verify.ocr import get_image_text
from datetime import date
import sys, pytz
from feed.align import face_angle_detect
from verify.barcode import barcode_valid
from verify.forensics import text_matches_name
import uuid
import os
from feed.middleware import get_current_request
from django.contrib import messages
from barcode.idscantext import decode_ocr

def get_uuid():
    id = "%s" % (uuid.uuid4())
    return id

import random
import jellyfish

def scan_id(verification, foreign, lang='eng'):
    print('Validating ID')
    self = verification
    id_path = verification.document_isolated.path
    new_ocr = get_image_text(id_path, lang=lang)
    verification.barcode_data = new_ocr
    verification.save()
    if not foreign: # and verification.user.profile.enable_facial_recognition:
        faces = verification.user.faces.all()
        if id_path == None or faces.count() == 0:
            return False
        if not verification.user.profile.disable_id_face_match and not verify_id_document(id_path, faces):
            print("Failed to verify document due to face mismatch.")
            return False
        if not verify_age(id_path):
            messages.warning(get_current_request(), 'You are not old enough to use the site, you must be at least {} to continue.'.format(settings.MIN_AGE_VERIFIED))
            print('ID failed photo age test')
            os.remove(id_path)
            return False
    print(new_ocr)
    if len(new_ocr) < 100:
        print('OCR Length is too short.')
        return False
    print("OCR length valid")
    if verification.user and verification.user.verifications.count() > 0:
        name = verification.user.verifications.last().full_name
        if not text_matches_name(new_ocr, name):
            print("Text doesnt match name '{}'".format(name))
            return False
        document_ocr = verification.user.scan.filter(side=True).last().barcode_data
        if document_ocr:
            dist = jellyfish.levenshtein_distance(document_ocr, new_ocr)
            print('Jellyfish is ' + str(dist))
            if dist > 450:
                print('Jellyfish distance is too great, {}'.format(dist))
                return False
    print('Validating birthday')
    birthday = None
    expiry = None
    try:
        birthday, expiry = text_has_valid_birthday_and_expiry(new_ocr)
        if not birthday:
            messages.warning(get_current_request(), 'The birthday or expiry could not be parsed from this ID.')
            return False
        else:
            print(str(birthday))
            verification.birthday = birthday
            if expiry:
                verification.expiry = expiry
            verification.save()
    except:
        messages.warning(get_current_request(), 'The birthday or expiry could not be parsed from this ID.')
        print(traceback.format_exc())
        return False
    if settings.USE_IDWARE and not decode_ocr(verification.barcode_data, verification):
        print('IDScan API failed.')
        return False
    verification.verified = True
    verification.save()
    return birthday, expiry
