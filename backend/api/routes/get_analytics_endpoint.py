from fastapi import APIRouter, HTTPException, Request, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from admin.execution_analytics import get_analytics
from schemas import ProfileSchema

from api.dependencies import require_admin

router = APIRouter(prefix="/analytics", tags=["Analytics"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.get("/get_execution_analytics")
@limiter.limit("100/minute")
async def endpoint_get_analytics(
    request: Request,
    profile: ProfileSchema = Depends(require_admin),
):
    """
    Retrieves all execution analytics. Admin only.
    """
    try:
        analytics: dict = get_analytics()

        logger.info("Got execution analytics for profile %s", profile.user_id)

        return {
            "status": "success",
            "result": analytics,
        }

    except Exception:
        logger.exception("Failed to retrieve analytics")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve analytics.",
        )