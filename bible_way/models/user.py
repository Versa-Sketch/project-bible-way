from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class AuthProviderChoices(models.TextChoices):
    EMAIL = 'EMAIL', 'Email'
    GOOGLE = 'GOOGLE', 'Google'
    BOTH = 'BOTH', 'Both'


class User(AbstractUser):
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
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
    is_email_verified = models.BooleanField(default=False)
    email_verification_otp = models.CharField(max_length=4, null=True, blank=True)
    otp_expiry = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.email})"


class UserFollowers(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    follower_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    followed_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.follower_id.username} follows {self.followed_id.username}"

