from fastapi import APIRouter, HTTPException, Request, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from database.repos import get_all_profiles
from schemas import ProfileSchema

from api.dependencies import require_admin

router = APIRouter(prefix="/admin", tags=["Profiles"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.get("/get_all_profiles")
@limiter.limit("100/minute")
async def endpoint_get_profiles(
    request: Request, 
    profile: ProfileSchema = Depends(require_admin)
    ):
    """
    Retrieves all profiles.
    """
    try:
        profiles: list[ProfileSchema] = get_all_profiles()

        logger.info(f"Got number of profiles: {len(profiles)}")

        return {
            "status": "success",
            "number_of_profiles": len(profiles),
            "result": profiles,
        }

    except Exception:
        logger.exception("Failed to retrieve profiles")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve profiles.",
        )