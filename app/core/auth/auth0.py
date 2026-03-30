import time
from dataclasses import dataclass
from typing import Any

import httpx
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings

bearer_scheme = HTTPBearer(auto_error=True)


@dataclass
class AuthenticatedUser:
    sub: str
    scopes: list[str]
    raw_token: dict[str, Any]


class Auth0JWTValidator:
    def __init__(self) -> None:
        self._jwks_cache: dict[str, Any] | None = None
        self._jwks_cache_expires_at = 0.0

    async def _get_jwks(self) -> dict[str, Any]:
        now = time.time()
        if self._jwks_cache is not None and now < self._jwks_cache_expires_at:
            return self._jwks_cache

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(settings.auth0_jwks_url)
            response.raise_for_status()
            self._jwks_cache = response.json()
            self._jwks_cache_expires_at = now + settings.auth0_jwks_ttl_seconds
            return self._jwks_cache

    async def validate_token(self, token: str) -> AuthenticatedUser:
        try:
            unverified_header = jwt.get_unverified_header(token)
        except JWTError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token header") from exc

        jwks = await self._get_jwks()
        rsa_key: dict[str, Any] = {}
        for key in jwks.get("keys", []):
            if key.get("kid") == unverified_header.get("kid"):
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }
                break

        if not rsa_key:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unable to find appropriate key")

        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=[settings.auth0_algorithms],
                audience=settings.auth0_audience,
                issuer=settings.auth0_issuer,
            )
        except JWTError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token validation failed") from exc

        scopes = payload.get("scope", "").split()
        return AuthenticatedUser(sub=payload["sub"], scopes=scopes, raw_token=payload)


validator = Auth0JWTValidator()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    auth_validator: Auth0JWTValidator = Depends(lambda: validator),
) -> AuthenticatedUser:
    return await auth_validator.validate_token(credentials.credentials)


def require_scopes(*required_scopes: str):
    async def checker(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        missing = [scope for scope in required_scopes if scope not in current_user.scopes]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required scopes: {', '.join(missing)}",
            )
        return current_user

    return checker
