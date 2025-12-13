"""
URL configuration for project_chat app.
"""

from django.urls import path
from project_chat.views import ChatFileUploadView

urlpatterns = [
    path('api/chat/upload/', ChatFileUploadView.as_view(), name='chat_file_upload'),
]

