from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from database.repos import update_role_to_admin
from schemas import UpdateData

router = APIRouter(prefix="/admin", tags=["Profile Role"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.post("/update-role/")
@limiter.limit("100/minute")
async def endpoint_update_role(request: Request, data: UpdateData):
    """
    Endpint that updates a user's role to admin
    """
    try:
        did_update = update_role_to_admin(
            user_id=data.user_id, 
            email=data.email
            )
        if not did_update:
            logger.info(f"Couldn't update role for: {data.email}")
            return JSONResponse(
                status_code=404,
                content={
                    "status": "failure",
                    "email": data.email
                },
            )
        
        logger.info(f"Updated role for: {data.email}")
        return JSONResponse(
                status_code=200,
                content={
                    "status": "success", 
                    "updated_role_email": data.email
                    },
            )

    except Exception as e:
        logger.error(f"Failed to update role: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update role")