from django.db import models
from .user import User


class ConversationTypeChoices(models.TextChoices):
    DIRECT = "DIRECT", "Direct Chat"
    GROUP = "GROUP", "Group Chat"


class Conversation(models.Model):
    type = models.CharField(
        max_length=10,
        choices=ConversationTypeChoices.choices
    )

    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="chat/groups/", blank=True, null=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_conversations",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        if self.type == ConversationTypeChoices.GROUP:
            return self.name or f"Group #{self.id}"
        return f"Direct chat #{self.id}"


class ConversationMember(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="conversation_memberships",
    )

    is_admin = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)

    # For quick unread counts etc.
    last_read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("conversation", "user")

    def __str__(self):
        return f"{self.user} in {self.conversation}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )

    text = models.TextField(blank=True)
    # you can handle multiple attachments with a separate model if needed
    file = models.FileField(upload_to="chat/files/", blank=True, null=True)

    # reply threading
    reply_to = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="replies",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)

    is_deleted_for_everyone = models.BooleanField(default=False)

    def __str__(self):
        return f"Message #{self.id} in {self.conversation_id}"


class MessageReadReceipt(models.Model):
    """
    Optional: per-user read status for each message.
    If you don't need this level of detail, you can remove this
    and just use ConversationMember.last_read_at.
    """
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="read_receipts",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="message_read_receipts",
    )
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("message", "user")

    def __str__(self):
        return f"{self.user} read {self.message_id}"

