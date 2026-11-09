import logging
from functools import lru_cache
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client, create_client

from database.repos import get_profile  
from schemas import ProfileSchema
from configs.settings import get_settings

logger = logging.getLogger(__name__)

# auto_error=False so a missing header gives us a 401 (FastAPI's default is 403)
bearer_scheme = HTTPBearer(auto_error=False)

settings = get_settings()

@lru_cache
def get_supabase_client() -> Client:
    return create_client(
        settings.database.supabase_project_url, 
        settings.database.supabase_publishable_key
        )


def get_current_profile(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> ProfileSchema:
    """
    Verify the Supabase JWT and return the caller's application profile.

    Raises:
        401: token missing, invalid, or expired.
        403: token is valid but the user has no profile.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 1. Verify the token with Supabase and get the user
    try:
        response = get_supabase_client().auth.get_user(credentials.credentials)
        user = response.user if response else None
    except Exception as exc:
        logger.warning("JWT verification failed: %s", exc)
        user = None

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Load the application profile for that user
    try:
        return get_profile(UUID(str(user.id)))
    except LookupError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No profile found for this user.",
        )


async def require_admin(
    profile: ProfileSchema = Depends(get_current_profile),
) -> ProfileSchema:
    if profile.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return profile