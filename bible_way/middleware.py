"""
Custom middleware to exempt API endpoints from CSRF protection.
"""
from django.utils.deprecation import MiddlewareMixin


class DisableCSRFForAPI(MiddlewareMixin):
    """
    Disable CSRF protection for API endpoints that use token authentication.
    """
    def process_request(self, request):
        # List of URL patterns that should be exempt from CSRF
        api_paths = [
            '/admin/',  # Exempt all admin API endpoints
            '/user/',
            '/post/',
            '/comment/',
            '/reaction/',
            '/prayer-request/',
            '/promotion/',
            '/verse/',
            '/books/',
            '/share/',
            '/s/',
            '/api/',  # Exempt all /api/ endpoints (chat, notifications, etc.)
        ]
        
        # Check if the request path starts with any API path
        if any(request.path.startswith(path) for path in api_paths):
            setattr(request, '_dont_enforce_csrf_checks', True)
        
        return None

