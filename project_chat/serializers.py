"""
Serializers for chat file uploads.

Defines request/response serializers for file upload endpoints.
"""

from rest_framework import serializers


class FileUploadResponseSerializer(serializers.Serializer):
    """Serializer for file upload success response."""
    file_url = serializers.URLField()
    file_type = serializers.CharField()
    file_size = serializers.IntegerField()
    file_name = serializers.CharField()


class FileUploadErrorSerializer(serializers.Serializer):
    """Serializer for file upload error response."""
    success = serializers.BooleanField(default=False)
    error = serializers.CharField()
    error_code = serializers.CharField()


class FileUploadSuccessSerializer(serializers.Serializer):
    """Serializer for file upload success response wrapper."""
    success = serializers.BooleanField(default=True)
    data = FileUploadResponseSerializer()

