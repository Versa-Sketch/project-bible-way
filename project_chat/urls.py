"""
URL configuration for project_chat app.
"""

from django.urls import path
from project_chat.views import ChatFileUploadView, get_conversation_view, get_inbox_view

urlpatterns = [
    path('upload/', ChatFileUploadView.as_view(), name='chat_file_upload'),
    path('conversation/<str:conversation_id>/', get_conversation_view, name='get_conversation'),
    path('inbox/', get_inbox_view, name='get_inbox'),
]

