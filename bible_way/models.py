from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# Enums
class LanguageChoices(models.TextChoices):
    ENGLISH = 'EN', 'English'
    SPANISH = 'ES', 'Spanish'
    FRENCH = 'FR', 'French'
    GERMAN = 'DE', 'German'
    ITALIAN = 'IT', 'Italian'
    PORTUGUESE = 'PT', 'Portuguese'
    RUSSIAN = 'RU', 'Russian'
    CHINESE_SIMPLIFIED = 'ZH_CN', 'Chinese (Simplified)'
    CHINESE_TRADITIONAL = 'ZH_TW', 'Chinese (Traditional)'
    JAPANESE = 'JA', 'Japanese'
    KOREAN = 'KO', 'Korean'
    ARABIC = 'AR', 'Arabic'
    HINDI = 'HI', 'Hindi'
    BENGALI = 'BN', 'Bengali'
    URDU = 'UR', 'Urdu'
    TURKISH = 'TR', 'Turkish'
    POLISH = 'PL', 'Polish'
    DUTCH = 'NL', 'Dutch'
    GREEK = 'EL', 'Greek'
    HEBREW = 'HE', 'Hebrew'
    SWEDISH = 'SV', 'Swedish'
    NORWEGIAN = 'NO', 'Norwegian'
    DANISH = 'DA', 'Danish'
    FINNISH = 'FI', 'Finnish'
    CZECH = 'CS', 'Czech'
    ROMANIAN = 'RO', 'Romanian'
    HUNGARIAN = 'HU', 'Hungarian'
    THAI = 'TH', 'Thai'
    VIETNAMESE = 'VI', 'Vietnamese'
    INDONESIAN = 'ID', 'Indonesian'
    MALAY = 'MS', 'Malay'
    TAGALOG = 'TL', 'Tagalog'
    SWAHILI = 'SW', 'Swahili'
    AMHARIC = 'AM', 'Amharic'
    YORUBA = 'YO', 'Yoruba'
    ZULU = 'ZU', 'Zulu'
    PERSIAN = 'FA', 'Persian'
    UKRAINIAN = 'UK', 'Ukrainian'
    TAMIL = 'TA', 'Tamil'
    TELUGU = 'TE', 'Telugu'
    MARATHI = 'MR', 'Marathi'
    GUJARATI = 'GU', 'Gujarati'

class CategoryChoices(models.TextChoices):
    SEGREGATE_BIBLES = 'SEGREGATE_BIBLES', 'Segregate Bibles'
    BIBLE_READER = 'BIBLE_READER', 'BibleReader'

class AgeGroupChoices(models.TextChoices):
    CHILDREN = 'CHILDREN', 'Children'
    TEEN = 'TEEN', 'Teen'
    ADULT = 'ADULT', 'Adult'
    SENIOR = 'SENIOR', 'Senior'

class ConversationTypeChoices(models.TextChoices):
    DIRECT = "DIRECT", "Direct Chat"
    GROUP = "GROUP", "Group Chat"

class AuthProviderChoices(models.TextChoices):
    EMAIL = 'EMAIL', 'Email'
    GOOGLE = 'GOOGLE', 'Google'
    BOTH = 'BOTH', 'Both'

# Create your models here.
class User(AbstractUser):
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user_name = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    country = models.CharField(max_length=255)
    age = models.IntegerField(null=True, blank=True)
    preferred_language = models.CharField(max_length=255, null=True, blank=True)
    auth_provider = models.CharField(
        max_length=10,
        choices=AuthProviderChoices.choices,
        default=AuthProviderChoices.EMAIL
    )
    google_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    profile_picture_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.user_name} ({self.email})"

class UserFollowers(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    follower_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    followed_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.follower_id.user_name} follows {self.followed_id.user_name}"

class Category(models.Model):
    category_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    category_name = models.CharField(
        max_length=35,
        choices=CategoryChoices.choices
    )

    def __str__(self):
        return self.get_category_name_display() 


class Language(models.Model):
    language_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    language_name = models.CharField(
        max_length=6,
        choices=LanguageChoices.choices,
        default=LanguageChoices.ENGLISH
    )

    def __str__(self):
        return self.get_language_name_display()

class AgeGroup(models.Model):
    age_group_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    age_group_name = models.CharField(
        max_length=10,
        choices=AgeGroupChoices.choices    
        )
    age_group_created_at = models.DateTimeField(auto_now_add=True)
    age_group_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_age_group_name_display()

class Module(models.Model):
    module_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='modules')
    url = models.URLField(max_length=255)
    text_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    age_group = models.ForeignKey(AgeGroup, on_delete=models.CASCADE, related_name='modules')
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='modules')
    metadata = models.JSONField(default=dict)

    def __str__(self):
        return self.title

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
