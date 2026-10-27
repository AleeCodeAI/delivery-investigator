from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from app.delivery_investigator import Investigator
from schemas import InputDataSchema, FinalResult

router = APIRouter(prefix="/master-pipeline", tags=["Master"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.post("/delivery-investigator-run")
@limiter.limit("50/minute")
async def endpoint_run_copilot(request: Request, input_data: InputDataSchema):
    """
    Triggers the master pipeline executor.
    Runs the retrieval and synthesis pipeline and returns the structured output.
    """
    try:
        investigator = Investigator()

        result: FinalResult = await investigator.run(
            input_data=input_data
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

    except Exception as e:
        logger.error(f"Failed to run executor: {e}")

        raise HTTPException(
            status_code=500,
            detail=f"Failed to run executor: {str(e)}",
        )