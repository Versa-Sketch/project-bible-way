from django.apps import AppConfig


class ProjectNotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'project_notifications'
    
    def ready(self):
        """Import signals when app is ready."""
        import project_notifications.signals.notification_signals  # noqa
