"""
WebSocket URL routing configuration.

Defines the WebSocket URL patterns for chat functionality.
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Unified user connection - recommended (handles all conversations for a user)
    re_path(r'^ws/user/$', consumers.UserChatConsumer.as_asgi()),
    
    # Per-conversation connection - legacy (one connection per conversation)
    re_path(r'ws/chat/(?P<conversation_id>[0-9a-f-]+)/$', consumers.ChatConsumer.as_asgi()),
]

