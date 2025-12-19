from django.db import models
import uuid
from .user import User


class Post(models.Model):
    post_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bible_way_post'

    def __str__(self):
        return f"Post {self.post_id} by {self.user}"

class Verse(models.Model):
    verse_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField(null=True, blank=True) 
    title = models.CharField(max_length=255, null=True, blank=True, default="Quote of the day") 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bible_way_verse'

    def __str__(self):
        return f"Verse {self.verse_id} - {self.title}"
    

class PrayerRequest(models.Model):
    prayer_request_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="prayer_requests")
    name = models.CharField(max_length=255, default="Anonymous")
    email = models.EmailField(default="anonymous@example.com")
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bible_way_prayer_request'

    def __str__(self):
        return f"Prayer Request {self.prayer_request_id} by {self.user}"


class Media(models.Model):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    MEDIA_TYPES = [
        (IMAGE, "Image"),
        (VIDEO, "Video"),
        (AUDIO, "Audio"),
    ]

    media_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="media",
        null=True,
        blank=True,
    )
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bible_way_media'

    def __str__(self):
        return f"Media {self.media_id} - {self.get_media_type_display()}"


class Comment(models.Model):
    comment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    prayer_request = models.ForeignKey(PrayerRequest, on_delete=models.CASCADE, related_name="comments", null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bible_way_comment'

    def __str__(self):
        return f"Comment {self.comment_id} by {self.user}"


class Reaction(models.Model):
    LIKE = "like"
    LOVE = "love"
    REACTION_TYPES = [
        (LIKE, "Like"),
        (LOVE, "Love"),
    ]

    reaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reactions")
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="reactions",
        null=True,
        blank=True,
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="reactions",
        null=True,
        blank=True,
    )
    prayer_request = models.ForeignKey(PrayerRequest, on_delete=models.CASCADE, related_name="reactions", null=True, blank=True)
    verse = models.ForeignKey(Verse, on_delete=models.CASCADE, related_name="reactions", null=True, blank=True)
    reaction_type = models.CharField(max_length=20, choices=REACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bible_way_reaction'

    def __str__(self):
        return f"Reaction {self.reaction_id} - {self.get_reaction_type_display()}"


class Share(models.Model):
    share_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="shares")
    shared_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shares_sent"
    )
    shared_to = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shares_received"
    )
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bible_way_share'

    def __str__(self):
        return f"Share {self.share_id} from {self.shared_by} to {self.shared_to}"


class Promotion(models.Model):
    promotion_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    redirect_link = models.URLField()
    meta_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bible_way_promotion'

    def __str__(self):
        return f"Promotion {self.promotion_id} - {self.title}"


class PromotionImage(models.Model):
    promotion_image_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    promotion = models.ForeignKey(
        Promotion,
        on_delete=models.CASCADE,
        related_name="promotion_images"
    )
    image_url = models.URLField()
    image_type = models.CharField(max_length=20, default="image")
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'bible_way_promotion_image'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"PromotionImage {self.promotion_image_id} for {self.promotion.title}"


class ShareLinkContentTypeChoices(models.TextChoices):
    POST = 'POST', 'Post'
    PROFILE = 'PROFILE', 'Profile'


class ShareLink(models.Model):
    share_token = models.CharField(max_length=20, unique=True, db_index=True)
    content_type = models.CharField(max_length=10, choices=ShareLinkContentTypeChoices.choices)
    content_id = models.UUIDField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="share_links_created")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'bible_way_share_link'
        indexes = [
            models.Index(fields=['share_token']),
            models.Index(fields=['content_type', 'content_id']),
        ]

    def __str__(self):
        return f"ShareLink {self.share_token} - {self.get_content_type_display()}"


class Wallpaper(models.Model):
    wallpaper_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image_url = models.URLField()
    filename = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bible_way_wallpaper'
        ordering = ['-created_at']

    def __str__(self):
        return f"Wallpaper {self.wallpaper_id} - {self.filename}"




