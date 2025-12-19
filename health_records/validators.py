"""
File upload validators for security
"""
from django.core.exceptions import ValidationError
from django.conf import settings
import os


def validate_image_file(value):
    """Validate uploaded image file"""
    # Check file size
    if value.size > settings.MAX_UPLOAD_SIZE:
        raise ValidationError(
            f'File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / (1024 * 1024):.0f}MB.'
        )
    
    # Check file extension
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f'File type not allowed. Allowed types: {", ".join(settings.ALLOWED_IMAGE_EXTENSIONS)}'
        )
    
    # Check MIME type (basic check - can be spoofed, but helps)
    if hasattr(value, 'content_type'):
        if value.content_type not in settings.ALLOWED_IMAGE_MIME_TYPES:
            raise ValidationError('File type not allowed.')


def validate_pdf_file(value):
    """Validate uploaded PDF file"""
    # Check file size
    if value.size > settings.MAX_UPLOAD_SIZE:
        raise ValidationError(
            f'File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / (1024 * 1024):.0f}MB.'
        )
    
    # Check file extension
    ext = os.path.splitext(value.name)[1].lower()
    if ext != '.pdf':
        raise ValidationError('Only PDF files are allowed.')
    
    # Check MIME type
    if hasattr(value, 'content_type'):
        if value.content_type != 'application/pdf':
            raise ValidationError('File must be a PDF.')

