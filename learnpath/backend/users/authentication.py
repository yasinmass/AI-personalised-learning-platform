"""
Custom JWT authentication for the API
"""
import jwt
from django.conf import settings
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User


class CustomJWTAuthentication(TokenAuthentication):
    """Custom JWT authentication to handle Bearer tokens"""
    
    def authenticate(self, request):
        """Authenticate the request using JWT token from Authorization header"""
        auth = request.META.get('HTTP_AUTHORIZATION', '').split()
        
        if not auth or auth[0].lower() != 'bearer':
            return None
        
        if len(auth) == 1:
            raise AuthenticationFailed('Invalid token header. No credentials provided.')
        
        if len(auth) > 2:
            raise AuthenticationFailed('Invalid token header. Token string should not contain spaces.')
        
        try:
            token = auth[1]
            # Decode the JWT token
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            if not user_id:
                raise AuthenticationFailed('Invalid token. No user ID found.')
            
            # Get the user from database
            user = User.objects.get(id=user_id)
            return (user, token)
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token.')
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found.')
        except Exception as e:
            raise AuthenticationFailed(f'Authentication error: {str(e)}')
