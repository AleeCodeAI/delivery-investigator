from fastapi import APIRouter, HTTPException, Request, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from database.repos import get_executions_by_user_id
from schemas import ProfileSchema, ExecutionSchema

from api.dependencies import get_current_profile

router = APIRouter(prefix="/history", tags=["History"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.get("/get_user_history")
@limiter.limit("50/minute")
async def endpoint_get_history(
    request: Request, 
    profile: ProfileSchema = Depends(get_current_profile)
    ):
    """
    Retrieves all execution history of a particular user.
    """
    try:
        histories: list[ExecutionSchema] = get_executions_by_user_id(user_id=profile.user_id)

        logger.info(f"Got number of histories: {len(histories)}")

        return {
            "status": "success",
            "number_of_histories": len(histories),
            "result": histories,
        }

    except Exception:
        logger.exception("Failed to retrieve user histories")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve histories.",
        )