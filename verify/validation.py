NUM_FACES = 9
MIN_DIST = 5

def verify_id_document(image_path, faces):
    from verify.blur_detection import detect_blur
    from django.contrib.auth.models import User
    import uuid
    from face.models import Face
    import face_recognition
    from face.deep import verify_face_score, verify_age, verify_emotion, is_face
    from django.conf import settings
    PASSING = settings.ID_FACE_PASSING_SCORE

    if detect_blur(image_path):
        return False
#    if not is_face(image_path):
#        return False
    if not verify_age(image_path):
        print("Age couldn't be verified")
        return False
    score = verify_face_score(image_path, faces)
    print(score)
    if score < PASSING:
        print("Couldn't verify face match on ID.")
        return False
    print('Verified face match on ID')
    return True
