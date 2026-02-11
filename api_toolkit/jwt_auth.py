"""
JWT Authentication Module.

Provides JWT token creation, validation, and refresh
functionality for API authentication.
"""

import time
import logging
from typing import Dict, Any, Optional

import jwt

logger = logging.getLogger(__name__)


class JWTAuth:
    """
    JWT-based authentication handler.

    Creates, validates, and refreshes JWT tokens with
    configurable expiration and algorithms.

    Args:
        secret_key: Secret key for signing tokens.
        algorithm: JWT signing algorithm (default: HS256).
        access_token_ttl: Access token TTL in seconds.
        refresh_token_ttl: Refresh token TTL in seconds.

    Example:
        >>> auth = JWTAuth(secret_key="my-secret")
        >>> token = auth.create_token({"user_id": "123"})
        >>> payload = auth.verify_token(token)
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_ttl: int = 1800,
        refresh_token_ttl: int = 604800,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_ttl = access_token_ttl
        self.refresh_token_ttl = refresh_token_ttl
        self._blacklist: set = set()

    def create_token(
        self,
        payload: Dict[str, Any],
        ttl: Optional[int] = None,
        token_type: str = "access",
    ) -> str:
        """
        Create a JWT token.

        Args:
            payload: Data to encode in the token.
            ttl: Custom TTL in seconds (overrides default).
            token_type: Token type ('access' or 'refresh').

        Returns:
            Encoded JWT string.
        """
        now = time.time()
        default_ttl = (
            self.access_token_ttl if token_type == "access"
            else self.refresh_token_ttl
        )

        token_data = {
            **payload,
            "iat": now,
            "exp": now + (ttl or default_ttl),
            "type": token_type,
        }

        token = jwt.encode(token_data, self.secret_key, algorithm=self.algorithm)
        logger.debug("Created %s token for payload: %s", token_type, payload)
        return token

    def verify_token(
        self, token: str, expected_type: str = "access"
    ) -> Dict[str, Any]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token string to verify.
            expected_type: Expected token type.

        Returns:
            Decoded token payload.

        Raises:
            jwt.InvalidTokenError: If token is invalid or expired.
            ValueError: If token type doesn't match or is blacklisted.
        """
        if token in self._blacklist:
            raise ValueError("Token has been revoked")

        payload = jwt.decode(
            token, self.secret_key, algorithms=[self.algorithm]
        )

        if payload.get("type") != expected_type:
            raise ValueError(
                f"Expected {expected_type} token, got {payload.get('type')}"
            )

        return payload

    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Create a new access token from a valid refresh token.

        Args:
            refresh_token: Valid refresh token.

        Returns:
            New access token string.
        """
        payload = self.verify_token(refresh_token, expected_type="refresh")

        # Remove refresh-specific fields
        new_payload = {
            k: v for k, v in payload.items()
            if k not in ("iat", "exp", "type")
        }

        return self.create_token(new_payload, token_type="access")

    def revoke_token(self, token: str) -> None:
        """Add a token to the blacklist."""
        self._blacklist.add(token)
        logger.info("Token revoked")

    def create_token_pair(self, payload: Dict[str, Any]) -> Dict[str, str]:
        """
        Create both access and refresh tokens.

        Args:
            payload: Data to encode in both tokens.

        Returns:
            Dict with 'access_token' and 'refresh_token' keys.
        """
        return {
            "access_token": self.create_token(payload, token_type="access"),
            "refresh_token": self.create_token(payload, token_type="refresh"),
        }