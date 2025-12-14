"""
URL configuration for project_chat app.
"""

from django.urls import path
from project_chat.views import ChatFileUploadView, get_conversation_view, get_inbox_view

urlpatterns = [
    path('api/chat/upload/', ChatFileUploadView.as_view(), name='chat_file_upload'),
    path('api/chat/conversation/<str:conversation_id>/', get_conversation_view, name='get_conversation'),
    path('api/chat/inbox/', get_inbox_view, name='get_inbox'),
]

