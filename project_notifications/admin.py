from django.contrib import admin
from project_notifications.models import Notification, NotificationFetchTracker


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('notification_id', 'recipient', 'notification_type', 'actor', 'created_at')
    list_filter = ('notification_type', 'created_at')
    search_fields = ('recipient__user_name', 'recipient__email', 'actor__user_name', 'actor__email')
    readonly_fields = ('notification_id', 'created_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('notification_id', 'recipient', 'notification_type', 'actor')
        }),
        ('Target Information', {
            'fields': ('target_id', 'target_type', 'conversation_id', 'message_id')
        }),
        ('Metadata', {
            'fields': ('metadata', 'created_at')
        }),
    )


@admin.register(NotificationFetchTracker)
class NotificationFetchTrackerAdmin(admin.ModelAdmin):
    list_display = ('tracker_id', 'user', 'last_fetch_at', 'updated_at')
    list_filter = ('last_fetch_at', 'updated_at')
    search_fields = ('user__user_name', 'user__email')
    readonly_fields = ('tracker_id', 'created_at', 'updated_at')
    ordering = ('-updated_at',)
