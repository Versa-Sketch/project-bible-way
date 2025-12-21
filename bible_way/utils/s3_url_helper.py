"""
S3 URL helper utilities for converting stored URLs to presigned URLs.

Provides functions to convert S3 URLs stored in the database to presigned URLs
for secure, time-limited access.
"""

import re
import boto3
from urllib.parse import urlparse
from django.conf import settings
from typing import List, Optional


def _extract_s3_key_from_url(url: str) -> str:
    """
    Extract S3 key from full S3 URL.
    
    Args:
        url: Full S3 URL like https://bucket.s3.region.amazonaws.com/key
        
    Returns:
        S3 key path
    """
    if not url:
        return ""
    
    # If it's already a key (no http/https), return as-is
    if not url.startswith(('http://', 'https://')):
        return url
    
    try:
        parsed = urlparse(url)
        # Remove leading slash from path
        key = parsed.path.lstrip('/')
        return key
    except Exception:
        # Fallback: try regex extraction
        match = re.search(r'\.s3\.[^/]+\.amazonaws\.com/(.+)$', url)
        if match:
            return match.group(1)
        return url


def _generate_presigned_url_internal(s3_key: str, expiration: int = None) -> str:
    """
    Generate presigned URL for S3 object.
    
    Args:
        s3_key: S3 key path or full S3 URL (will extract key if URL provided)
        expiration: Expiration time in seconds (defaults to AWS_S3_PRESIGNED_URL_EXPIRATION setting)
        
    Returns:
        Presigned URL string
    """
    if not s3_key:
        return ""
    
    # Extract key if full URL provided
    key = _extract_s3_key_from_url(s3_key)
    
    if not key:
        return s3_key  # Return original if extraction fails
    
    # Use default expiration from settings if not provided
    if expiration is None:
        expiration = getattr(settings, 'AWS_S3_PRESIGNED_URL_EXPIRATION', 3600)
    
    try:
        # Create S3 client
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': key},
            ExpiresIn=expiration
        )
        return presigned_url
    except Exception as e:
        # If presigned URL generation fails, return original URL/key
        # This ensures backward compatibility
        return s3_key


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
        return _generate_presigned_url_internal(url_or_key, expiration)
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

