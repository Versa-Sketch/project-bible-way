"""
URL configuration for project_notifications app.
"""

from django.urls import path
from project_notifications.views import get_missed_notifications_view, mark_all_notifications_read_view

urlpatterns = [
    path('missed/', get_missed_notifications_view, name='get_missed_notifications'),
    path('markread/', mark_all_notifications_read_view, name='mark_all_notifications_read'),
]

