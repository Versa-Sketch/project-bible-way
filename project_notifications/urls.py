"""
URL configuration for project_notifications app.
"""
from django.urls import path
from project_notifications.views import get_notifications_view

urlpatterns = [
    path('', get_notifications_view, name='get_notifications'),
]
