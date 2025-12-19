"""
Security middleware for rate limiting and security logging
"""
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger('django.security')


class RateLimitMiddleware:
    """
    Simple rate limiting middleware
    For production, consider using django-ratelimit or django-axes
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Rate limits: (max_requests, time_window_seconds)
        self.rate_limits = {
            '/accounts/login/': (5, 300),  # 5 attempts per 5 minutes
            '/clinicians/send-practitioner-code/': (10, 3600),  # 10 emails per hour
        }

    def __call__(self, request):
        # Check rate limits for specific paths
        path = request.path
        for limit_path, (max_requests, window) in self.rate_limits.items():
            if path.startswith(limit_path):
                if self.is_rate_limited(request, limit_path, max_requests, window):
                    logger.warning(
                        f'Rate limit exceeded for {request.user} at {path}',
                        extra={'request': request}
                    )
                    return HttpResponseForbidden(
                        'Too many requests. Please try again later.'
                    )
        
        response = self.get_response(request)
        return response

    def is_rate_limited(self, request, path, max_requests, window):
        """Check if request exceeds rate limit"""
        # Use IP address as identifier
        ip_address = self.get_client_ip(request)
        cache_key = f'rate_limit:{path}:{ip_address}'
        
        # Get current count
        current_count = cache.get(cache_key, 0)
        
        if current_count >= max_requests:
            return True
        
        # Increment count
        cache.set(cache_key, current_count + 1, window)
        return False

    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware:
    """
    Add security headers to responses
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Content Security Policy (adjust based on your needs)
        # This is a restrictive CSP - adjust as needed
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # unsafe-inline/eval needed for Django admin
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: blob:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response['Content-Security-Policy'] = csp
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy (formerly Feature Policy)
        response['Permissions-Policy'] = (
            'geolocation=(), microphone=(), camera=()'
        )
        
        return response

