from django.db import models
import uuid
from bible_way.models import User


class NotificationTypeChoices(models.TextChoices):
    FOLLOW = "FOLLOW", "Follow"
    POST_LIKE = "POST_LIKE", "Post Like"
    COMMENT_LIKE = "COMMENT_LIKE", "Comment Like"
    PRAYER_REQUEST_LIKE = "PRAYER_REQUEST_LIKE", "Prayer Request Like"
    VERSE_LIKE = "VERSE_LIKE", "Verse Like"
    NEW_MESSAGE = "NEW_MESSAGE", "New Message"
    COMMENT_ON_POST = "COMMENT_ON_POST", "Comment on Post"
    COMMENT_ON_PRAYER_REQUEST = "COMMENT_ON_PRAYER_REQUEST", "Comment on Prayer Request"


class Notification(models.Model):
    notification_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationTypeChoices.choices
    )
    actor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="actions_triggered",
        null=True,
        blank=True
    )
    target_id = models.CharField(
        max_length=255,
        help_text="ID of the target object (post_id, comment_id, etc.)"
    )
    target_type = models.CharField(
        max_length=50,
        help_text="Type of target (post, comment, message, etc.)"
    )
    conversation_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="For message notifications"
    )
    message_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="For message notifications"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="For storing aggregated data (actors_count, actors list, last_actor_id)"
    )

    class Meta:
        db_table = 'project_notifications_notification'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'created_at']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Notification {self.notification_id} - {self.notification_type} for {self.recipient}"


class NotificationFetchTracker(models.Model):
    """Tracks when each user last fetched their notifications."""
    tracker_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="notification_fetch_tracker"
    )
    last_fetch_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_notifications_fetch_tracker'
        indexes = [
            models.Index(fields=['user', 'last_fetch_at']),
        ]

    def __str__(self):
        return f"FetchTracker for {self.user.user_name} - Last fetch: {self.last_fetch_at}"
