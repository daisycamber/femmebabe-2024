# face/face.py
NUM_FACES = 3
MIN_DIST = 0.65
MAX_ANGLE = 90

def is_face_user(image_path, user):
    from django.contrib.auth.models import User
    import uuid, cv2, os
    from .models import Face
    import face_recognition
    from .deep import verify_face, verify_age, verify_emotion, is_face
    from .gesturerecognizer import validate_gesture
    from .blur_detection import detect_blur
#    from .apis import is_safe
    from stacktrace.exceptions import VisitorDoesntUseSecretGestureException
    from feed.middleware import get_current_request
    from feed.templatetags.app_filters import nts
    from django.contrib import messages
    from face.antispoofing.liveness import is_live
    from feed.align import face_rotation_detect, has_features
    from sewar.full_ref import mse
    from face.template import is_template
    from .similar import similarity
    from face.smile import get_smile
    from feed.templatetags.nts import nts as number_to_string
    from PIL import Image
    import hashlib
    from feed.nude import is_nude
    r = get_current_request()
    image = Image.open(image_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')
        image.save(image_path)
    if detect_blur(image_path):
        messages.warning(r, 'Your photo is blurry. Please submit a new one.')
        print('Blurry face')
        return False
    if not is_face(image_path):
        messages.warning(r, 'There is no face in this photo.')
        print('Not a face!')
        return False
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    if len(face_locations) > 1 or len(face_locations) < 1:
        messages.warning(r, 'Only one face can be accepted in order to complete a login. {} faces were detected.'.format(nts(len(face_locations)).capitalize()))
        return False
#    if not is_safe(image_path):
#        messages.warning(r, 'You have failed the moderation workflow. You may be offensive, armed, or too young to use the site. Please do not continue.')
#        print('Face failed sightengine')
#        return False
    if not verify_age(image_path):
        messages.warning(r, 'You are not old enough to use the site, you must be at least {} to continue.'.format(settings.MIN_AGE))
        print('Face failed age test')
        os.remove(image_path)
        return False
    if is_nude(image_path) and not user.profile.vendor:
        print('Nudity')
        messages.warning(r, 'Please authenticate without displaying nudity.')
        os.remove(image_path)
        return False
    if abs(face_rotation_detect(image_path, False, True)) > MAX_ANGLE:
        messages.warning(r, 'Keep your face straight! We detected your face at an angle.')
        return False
#    if not verify_emotion(image_path):
#        print('Face failed emotion test')
#        return False
    if validate_gesture(image_path):
        messages.warning(r, 'Please keep your hands out of the photo.')
        print('Face failed gesture test')
        return False
#    if not has_features(image_path):
#        messages.warning(r, 'We couldn\'t detect your eyes, nose and/or mouth. Please remove any face coverings like a mask or sunglasses.')
#        print('Face failed cover test')
#        return False
#    if not get_smile(image_path):
#        messages.warning(r, 'Smile for the camera! We couldn\'t detect your smile.')
#        return False
    if not is_live(image_path):
        messages.warning(r, 'This photo isn\'t live. Please take a photo of your face, oriented towards the camera.')
        print('Not live!')
        return False
    if user:
        unknown_image = image
        user_encodings = list()
        user_faces = Face.objects.filter(user=user, authentic=True).order_by('-timestamp')
        hash_keys = dict()
        with open(image_path, 'rb') as f:
            filehash = hashlib.md5(f.read()).hexdigest()
        hash_keys[filehash] = 0
        for face in user_faces:
            filehash = ''
            if not face.hash and face.image and os.path.isfile(face.image.path):
                with open(face.image.path, 'rb') as f:
                    filehash = hashlib.md5(f.read()).hexdigest()
                face.hash = filehash
                face.save()
            elif face.hash:
                filehash = face.hash
            if not filehash in hash_keys:
                hash_keys[filehash] = face.id
            else:
                print("Duplicate face image hash")
                return False
        for face in user_faces[:32]:
            if open(face.image.path,"rb").read() == open(image_path,"rb").read():
                print("Duplicate face image")
                return False
#            if is_template(image_path, face.image.path) or is_template(face.image.path, image_path):
#                print('This photo is a template (an photo embedded in a photo) and cannot be accepted.')
#                return False
            if similarity(face.image.path, image_path):
                messages.warning(r, 'This photo is too similar to one previously uploaded.')
                return False
        if user_faces.count() > NUM_FACES:
            user_faces = user_faces[:NUM_FACES]
        for face in user_faces:
            image = face_recognition.load_image_file(face.image.path)
            image_encoding = face_recognition.face_encodings(image)[0]
            user_encodings.append(image_encoding)
        unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
        face_distances = face_recognition.face_distance(user_encodings, unknown_encoding)
        for dist in face_distances:
            if dist > MIN_DIST:
                print("Distance too great")
                messages.warning(r, 'Your face is too far from the camera.')
                return False
        if not user.profile.enable_facial_recognition and not user.profile.vendor and not user.is_superuser:
            print('Accepted face bypassing facial recognition')
            return True
        if user.faces.count() > 0:
            results = face_recognition.compare_faces(user_encodings, unknown_encoding)
            if results[0]:
                if not verify_face(image_path, user_faces):
                    messages.warning(r, 'Your face doesn\'t match our {} records with DeepFace. Please try again.'.format(number_to_string(user.faces.count())))
                    return False
                return True
        elif user.faces.count() == 0:
            return True
        messages.warning(r, 'Your face doesn\'t match our {} records with dlib. Please try again.'.format(number_to_string(user.faces.count())))
        return False
    else: return True
    return False
