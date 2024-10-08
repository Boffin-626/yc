import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import messaging.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yc.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            messaging.routing.websocket_urlpatterns
        )
    ),
})
