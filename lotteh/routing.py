from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.sessions import SessionMiddlewareStack
from django.urls import path
from shell import consumers as shell_consumers
from live import consumers as live_consumers
from vibe import consumers as vibe_consumers
from chat import consumers as chat_consumers
from chat import video_consumers as video_consumers
from photobooth import consumers as photobooth_consumers
from remote import consumers as remote_consumers
from games import consumers as games_consumers
from meet import consumers as meet_consumers
from security import consumers as security_consumers
from users import consumers as auth_consumers
from kick import consumers as kick_consumers
from desktop import consumers as desktop_consumers
from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

# URLs that handle the WebSocket connection are placed here.
websocket_urlpatterns = [
    path('ws/terminal/websocket/', shell_consumers.TerminalConsumer.as_asgi()),
    path('ws/shell/websocket/', shell_consumers.ShellConsumer.as_asgi()),
    path('ws/remote/', remote_consumers.RemoteConsumer.as_asgi()),
    path('ws/live/remote/<str:username>/<str:name>/', live_consumers.RemoteConsumer.as_asgi()),
    path('ws/live/camera/<str:username>/<str:name>/', live_consumers.CameraConsumer.as_asgi()),
    path('ws/live/video/<str:username>/<str:name>/', live_consumers.VideoConsumer.as_asgi()),
    path('ws/photobooth/remote/<str:username>/<str:name>/', photobooth_consumers.PhotoboothRemoteConsumer.as_asgi()),
    path('ws/photobooth/<str:username>/<str:name>/', photobooth_consumers.PhotoboothConsumer.as_asgi()),
    path('ws/chat/video/', video_consumers.VideoConsumer.as_asgi()),
    path('ws/chat/text/<str:username>/', chat_consumers.ChatConsumer.as_asgi()),
    path('ws/vibe/remote/receive/<str:username>/', vibe_consumers.RemoteReceiveConsumer.as_asgi()),
    path('ws/vibe/remote/send/', vibe_consumers.RemoteConsumer.as_asgi()),
    path('ws/games/<str:id>/<str:code>/', games_consumers.GameConsumer.as_asgi()),
    path('ws/meet/', meet_consumers.MeetingConsumer.as_asgi()),
    path('ws/security/modal/', security_consumers.ModalConsumer.as_asgi()),
    path('ws/auth/', auth_consumers.AuthConsumer.as_asgi()),
    path('ws/kick/', kick_consumers.KickConsumer.as_asgi()),
    path('ws/desktop/', desktop_consumers.DesktopConsumer.as_asgi()),
]

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            AllowedHostsOriginValidator(
                SessionMiddlewareStack(
                    URLRouter(websocket_urlpatterns)
                )
            ),
        ),
    }
)
