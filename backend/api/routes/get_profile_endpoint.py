import logging

from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from api.dependencies import get_current_profile
from schemas import ProfileSchema

router = APIRouter(tags=["Profile"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.get("/me")
@limiter.limit("100/minute")
async def endpoint_get_profile(
    request: Request,
    profile: ProfileSchema = Depends(get_current_profile),
):
    """Returns the caller's own profile (name, email, role)."""
    return {"status": "success", "result": profile}