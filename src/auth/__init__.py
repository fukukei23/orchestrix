"""Authentication module"""

from .jwt_handler import create_access_token, decode_access_token, verify_password, get_password_hash
from .dependencies import get_current_user
from .routes import router

__all__ = ['create_access_token', 'decode_access_token', 'verify_password', 'get_password_hash', 'get_current_user', 'router']