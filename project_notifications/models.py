from django.db import models
from django.conf import settings
import uuid


class NotificationTypeChoices(models.TextChoices):
    FOLLOW = 'FOLLOW', 'Follow'
    POST_LIKE = 'POST_LIKE', 'Post Like'
    COMMENT_LIKE = 'COMMENT_LIKE', 'Comment Like'
    PRAYER_REQUEST_LIKE = 'PRAYER_REQUEST_LIKE', 'Prayer Request Like'
    VERSE_LIKE = 'VERSE_LIKE', 'Verse Like'
    NEW_MESSAGE = 'NEW_MESSAGE', 'New Message'
    COMMENT_ON_POST = 'COMMENT_ON_POST', 'Comment on Post'
    COMMENT_ON_PRAYER_REQUEST = 'COMMENT_ON_PRAYER_REQUEST', 'Comment on Prayer Request'
    PRAYER_REQUEST_CREATED = 'PRAYER_REQUEST_CREATED', 'Prayer Request Created'


class Notification(models.Model):
    notification_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationTypeChoices.choices
    )
    target_id = models.CharField(
        max_length=255,
        help_text='ID of the target object (post_id, comment_id, etc.)'
    )
    target_type = models.CharField(
        max_length=50,
        help_text='Type of target (post, comment, message, etc.)'
    )
    conversation_id = models.IntegerField(
        blank=True,
        null=True,
        help_text='For message notifications'
    )
    message_id = models.IntegerField(
        blank=True,
        null=True,
        help_text='For message notifications'
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='actions_triggered',
        blank=True,
        null=True
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    metadata = models.JSONField(
        blank=True,
        default=dict,
        help_text='For storing aggregated data (actors_count, actors list, last_actor_id)'
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'project_notifications_notification'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'created_at']),
            models.Index(fields=['notification_type', 'target_id', 'recipient']),
            models.Index(fields=['recipient', 'is_read']),
        ]

    def __str__(self):
        return f"{self.notification_type} - {self.recipient.user_name}"


class NotificationFetchTracker(models.Model):
    tracker_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_fetch_tracker'
    )
    last_fetch_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_notifications_fetch_tracker'
        indexes = [
            models.Index(fields=['user', 'last_fetch_at']),
        ]

    def __str__(self):
        return f"Fetch tracker for {self.user.user_name}"

