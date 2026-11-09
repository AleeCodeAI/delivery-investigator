from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from database.repos import insert_invitation
from schemas import ProfileSchema

from api.dependencies import require_admin

router = APIRouter(prefix="/admin", tags=["Invitation"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.post("/insert-invitation")
@limiter.limit("50/minute")
async def endpoint_insert_invitation(
    request: Request, 
    name: str,
    email: str,
    profile: ProfileSchema = Depends(require_admin)
    ):
    """
    Triggers the master pipeline delivery investigator.
    Runs the agent and recommender pipeline and returns the structured output.
    """
    try:
        access_key = insert_invitation(
            name=name,
            email=email
        )

        logger.info("Invitation Insertion completed")

        data = {
            "access_key": str(access_key)
        }

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "result": data,
            },
        )

    except Exception:
        logger.exception("Failed to insert invitation")

        raise HTTPException(
            status_code=500,
            detail="The Invitation Insertion could not be completed. Please try again later.",
        )