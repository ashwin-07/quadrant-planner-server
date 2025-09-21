"""
JWT Token Handler for Google OAuth Integration
"""

import jwt
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from api.shared.exceptions import UnauthorizedError

logger = logging.getLogger(__name__)


class JWTTokenHandler:
    """Handle JWT token validation and user extraction for Google OAuth"""
    
    def __init__(self):
        # Google's public keys for JWT verification
        # In production, these should be fetched from Google's JWKS endpoint
        self.google_public_keys = {
            # This is a placeholder - in production, fetch from:
            # https://www.googleapis.com/oauth2/v3/certs
        }
    
    async def verify_google_token(self, token: str) -> Dict[str, Any]:
        """
        Verify Google OAuth JWT token and extract user information
        
        Args:
            token: JWT token from Authorization header
            
        Returns:
            Dict containing user information from token
            
        Raises:
            UnauthorizedError: If token is invalid or expired
        """
        try:
            # For development, we'll decode without verification
            # In production, you should verify the signature with Google's public keys
            decoded_token = jwt.decode(
                token, 
                options={"verify_signature": False},  # Skip signature verification for now
                algorithms=["RS256"]
            )
            
            # Validate token structure
            if not self._validate_token_structure(decoded_token):
                raise UnauthorizedError("Invalid token structure")
            
            # Check token expiration
            if self._is_token_expired(decoded_token):
                raise UnauthorizedError("Token has expired")
            
            # Extract user information
            user_info = self._extract_user_info(decoded_token)
            
            logger.info(f"Successfully verified token for user: {user_info.get('user_id')}")
            return user_info
            
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            raise UnauthorizedError("Invalid token format")
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise UnauthorizedError("Token verification failed")
    
    def _validate_token_structure(self, decoded_token: Dict[str, Any]) -> bool:
        """Validate that the token has required Google OAuth fields"""
        required_fields = ['iss', 'aud', 'sub', 'exp', 'iat']
        return all(field in decoded_token for field in required_fields)
    
    def _is_token_expired(self, decoded_token: Dict[str, Any]) -> bool:
        """Check if the token has expired"""
        exp_timestamp = decoded_token.get('exp')
        if not exp_timestamp:
            return True
        
        current_time = datetime.utcnow().timestamp()
        return current_time > exp_timestamp
    
    def _extract_user_info(self, decoded_token: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user information from the decoded token"""
        # Google OAuth token structure
        user_id = decoded_token.get('sub')  # Google user ID
        email = decoded_token.get('email', '')
        name = decoded_token.get('name', '')
        picture = decoded_token.get('picture', '')
        
        if not user_id:
            raise UnauthorizedError("User ID not found in token")
        
        return {
            'user_id': user_id,
            'email': email,
            'name': name,
            'picture': picture,
            'token_issued_at': decoded_token.get('iat'),
            'token_expires_at': decoded_token.get('exp')
        }


# Global instance
jwt_handler = JWTTokenHandler()


async def get_current_user_from_token(authorization: str) -> str:
    """
    Extract user ID from Authorization Bearer token
    
    Args:
        authorization: Authorization header value (e.g., "Bearer <token>")
        
    Returns:
        User ID from the token
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract token from "Bearer <token>" format
    try:
        scheme, token = authorization.split(' ', 1)
        if scheme.lower() != 'bearer':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme. Use 'Bearer'",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Use 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Verify token and extract user info
        user_info = await jwt_handler.verify_google_token(token)
        return user_info['user_id']
        
    except UnauthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_info(authorization: str) -> Dict[str, Any]:
    """
    Extract full user information from Authorization Bearer token
    
    Args:
        authorization: Authorization header value (e.g., "Bearer <token>")
        
    Returns:
        Dict containing user information
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract token from "Bearer <token>" format
    try:
        scheme, token = authorization.split(' ', 1)
        if scheme.lower() != 'bearer':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme. Use 'Bearer'",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Use 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Verify token and extract user info
        user_info = await jwt_handler.verify_google_token(token)
        return user_info
        
    except UnauthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
