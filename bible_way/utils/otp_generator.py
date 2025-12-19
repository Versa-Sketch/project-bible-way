import random
from datetime import timedelta
from django.utils import timezone
import os


def generate_otp() -> str:
    """
    Generate a 4-digit OTP code (0000-9999)
    """
    return str(random.randint(0, 9999)).zfill(4)


def get_otp_expiry() -> timezone.datetime:
    """
    Get OTP expiry time (default: 15 minutes from now)
    """
    expiry_minutes = int(os.getenv('ZEPTOMAIL_OTP_EXPIRY_MINUTES', '15'))
    return timezone.now() + timedelta(minutes=expiry_minutes)

