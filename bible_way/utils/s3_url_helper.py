"""
S3 URL helper utilities for converting stored URLs to presigned URLs.

Provides functions to convert S3 URLs stored in the database to presigned URLs
for secure, time-limited access.
"""

from django.conf import settings
from bible_way.storage.s3_utils import generate_presigned_url, extract_s3_key_from_url
from typing import List, Optional


def get_presigned_url(url_or_key: str, expiration: Optional[int] = None) -> str:
    """
    Convert S3 URL or key to presigned URL.
    
    Args:
        url_or_key: Full S3 URL or S3 key path
        expiration: Expiration time in seconds (defaults to AWS_S3_PRESIGNED_URL_EXPIRATION setting)
        
    Returns:
        Presigned URL if presigned URLs are enabled, otherwise returns original URL
    """
    if not url_or_key:
        return ""
    
    # Check if presigned URLs are enabled
    use_presigned = getattr(settings, 'AWS_S3_USE_PRESIGNED_URLS', True)
    
    if not use_presigned:
        return url_or_key
    
    # Use default expiration from settings if not provided
    if expiration is None:
        expiration = getattr(settings, 'AWS_S3_PRESIGNED_URL_EXPIRATION', 3600)
    
    try:
        return generate_presigned_url(url_or_key, expiration)
    except Exception:
        # If generation fails, return original URL for backward compatibility
        return url_or_key


def get_presigned_urls(urls: List[str], expiration: Optional[int] = None) -> List[str]:
    """
    Batch convert multiple S3 URLs to presigned URLs.
    
    Args:
        urls: List of S3 URLs or keys
        expiration: Expiration time in seconds (defaults to AWS_S3_PRESIGNED_URL_EXPIRATION setting)
        
    Returns:
        List of presigned URLs (or original URLs if presigned URLs disabled or generation fails)
    """
    if not urls:
        return []
    
    return [get_presigned_url(url, expiration) for url in urls]

