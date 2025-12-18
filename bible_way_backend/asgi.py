"""
ASGI config for bible_way_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bible_way_backend.settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# Import WebSocket routing and JWT middleware after Django setup
from project_chat.websocket.routing import websocket_urlpatterns as chat_websocket_urlpatterns
from project_chat.websocket.middleware import JWTAuthMiddlewareStack

# Unified WebSocket URL patterns (notifications are handled through ws/user/)
all_websocket_urlpatterns = chat_websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddlewareStack(
        URLRouter(all_websocket_urlpatterns)
    ),
})
