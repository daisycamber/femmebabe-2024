from live.models import VideoCamera
from django.urls import reverse
import uuid

def get_guest_camera(user):
    camera = Camera.objects.create(name=str(uuid.uuid4), user=user, key=str(uuid.uuid4()), public=False, recording=False, live=True, use_websocket=True, default=True, upload=True)
    return (reverse('live:golivevideo') + '?camera={}&key={}'.format(camera.name, camera.key), reverse('live:livevideo', kwargs={'username': user.profile.name}) + '?camera={}&key={}'.format(camera.name, camera.key))
