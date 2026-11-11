from fastapi import APIRouter, HTTPException, Request, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from database.repos import get_invitations
from schemas import ProfileSchema, InvitationSchema

from api.dependencies import require_admin

router = APIRouter(prefix="/admin", tags=["Invitation"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.get("/get_all_invitation")
@limiter.limit("100/minute")
async def endpoint_get_invitations(
    request: Request, 
    profile: ProfileSchema = Depends(require_admin)
    ):
    """
    Retrieves all invitations.
    """
    try:
        invitations: list[InvitationSchema] = get_invitations()

        logger.info(f"Got number of invitations: {len(invitations)}")

        return {
            "status": "success",
            "number_of_histories": len(invitations),
            "result": invitations,
        }

    except Exception:
        logger.exception("Failed to retrieve invitations")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve invitations.",
        )