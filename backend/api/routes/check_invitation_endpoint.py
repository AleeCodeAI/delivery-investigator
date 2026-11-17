from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from database.repos import check_invitation
from schemas import CheckData

router = APIRouter(prefix="/check", tags=["Invitation"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.post("/check-invitation/")
@limiter.limit("100/minute")
async def endpoint_check_invitation(
    request: Request, 
    data: CheckData
    ):
    """
    Endpoint that checks an invitation of a user
    """
    try:
        is_valid = check_invitation(
            access_key=data.access_key, 
            email=data.email
            )
        
        logger.info(f"Invitation validated successfully for: {data.email}")
        return JSONResponse(
                status_code=200,
                content={
                    "status": "success", 
                    "is_valid": is_valid,
                    "checked_invitation_email": data.email
                    },
            )

    except Exception as e:
        logger.error(f"Failed to check invitation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check invitation")