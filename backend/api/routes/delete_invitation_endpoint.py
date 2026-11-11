from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from database.repos import delete_invitation
from schemas import DeleteData

router = APIRouter(prefix="/admin", tags=["Invitation"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.delete("/delete-invitation/")
@limiter.limit("100/minute")
async def endpoint_delete_invitation(request: Request, data: DeleteData):
    """
    Endpoint that deletes an invitation of a user
    """
    try:
        did_delete = delete_invitation(
            access_key=data.access_key, 
            email=data.email
            )
        if not did_delete:
            logger.info(f"Couldn't delete invitation for: {data.email}")
            return JSONResponse(
                status_code=404,
                content={
                    "status": "failure",
                    "email": data.email
                },
            )
        
        logger.info(f"Deleted invitation for: {data.email}")
        return JSONResponse(
                status_code=200,
                content={
                    "status": "success", 
                    "deleted_invitation_email": data.email
                    },
            )

    except Exception as e:
        logger.error(f"Failed to delete invitation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete invitation")