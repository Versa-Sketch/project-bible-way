"""
JWT Authentication Middleware for WebSocket connections.

This middleware extracts JWT tokens from the query string and validates them,
setting the user in the scope for authenticated connections.
"""

from urllib.parse import parse_qs
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token_string):
    """
    Validate JWT token and return the associated user.
    
    Args:
        token_string: The JWT token string
        
    Returns:
        User object if token is valid, None otherwise
    """
    try:
        # Validate token
        UntypedToken(token_string)
        
        # Get user_id from token
        from rest_framework_simplejwt.tokens import AccessToken
        access_token = AccessToken(token_string)
        user_id = access_token.get('user_id')
        
        if not user_id:
            return None
            
        # Get user from database
        try:
            user = User.objects.get(user_id=user_id, is_active=True)
            return user
        except User.DoesNotExist:
            return None
            
    except (TokenError, InvalidToken, Exception):
        return None


class JWTAuthMiddleware(BaseMiddleware):
    """
    Middleware to authenticate WebSocket connections using JWT tokens.
    
    Token should be provided in query string: ws://domain/ws/user/?token=eyJ...
    """
    
    async def __call__(self, scope, receive, send):
        # Extract token from query string
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]
        
        if not token:
            # No token provided, set anonymous user
            scope['user'] = None
        else:
            # Validate token and get user
            user = await get_user_from_token(token)
            scope['user'] = user
        
        return await super().__call__(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    """
    Stack JWT auth middleware with the inner application.
    """
    return JWTAuthMiddleware(inner)

