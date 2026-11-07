from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from app.delivery_investigator import Investigator
from schemas import InputDataSchema, FinalResult, ProfileSchema

from api.dependencies import get_current_profile

router = APIRouter(prefix="/master-pipeline", tags=["Master"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.post("/delivery-investigator-run")
@limiter.limit("50/minute")
async def endpoint_run_investigator(
    request: Request, 
    input_data: InputDataSchema,
    profile: ProfileSchema = Depends(get_current_profile)
    ):
    """
    Triggers the master pipeline delivery investigator.
    Runs the agent and recommender pipeline and returns the structured output.
    """
    try:
        investigator = Investigator()

        result: FinalResult = await investigator.run(
            input_data=input_data,
            user_id=profile.user_id
        )

        # Pipeline successfully generated a result
        logger.info(
            f"Delivery Investigator finished; investigation completed: "
            f"{'True' if result.agent_result.investigation_success else 'False'}"
        )

        data = {
            "agent_result": result.agent_result.model_dump(mode='json'),
            "recommender_result": result.recommender_result.model_dump(mode='json'),
        }

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "investigation_success": (
                    "True"
                    if result.agent_result.investigation_success
                    else "False"
                ),
                "result": data,
            },
        )

    except Exception:
        logger.exception("Failed to run delivery investigator")

        raise HTTPException(
            status_code=500,
            detail="The investigation could not be completed. Please try again later.",
        )