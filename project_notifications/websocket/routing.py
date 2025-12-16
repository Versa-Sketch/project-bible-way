"""
WebSocket URL routing configuration for notifications.

Defines the WebSocket URL patterns for notification functionality.
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # User notification connection
    re_path(r'^ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]

