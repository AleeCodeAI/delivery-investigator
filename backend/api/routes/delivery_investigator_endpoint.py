from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from app.delivery_investigator import Investigator
from schemas import InputDataSchema, FinalResult, ProfileSchema
from database.repos import get_specific_execution

from api.dependencies import get_current_profile

router = APIRouter(prefix="/master-pipeline", tags=["Master"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


def build_response(result: FinalResult, cached: bool) -> JSONResponse:
    """Build the API response; used by both cache hits and fresh runs."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "cached": cached,
            "investigation_success": (
                "True" if result.agent_result.investigation_success else "False"
            ),
            "result": {
                "agent_result": result.agent_result.model_dump(mode="json"),
                "recommender_result": result.recommender_result.model_dump(mode="json"),
            },
        },
    )


@router.post("/delivery-investigator-run")
@limiter.limit("50/minute")
async def endpoint_run_investigator(
    request: Request,
    input_data: InputDataSchema,
    profile: ProfileSchema = Depends(get_current_profile),
):
    """
    Triggers the master pipeline delivery investigator.
    Returns a cached result if a recent successful execution exists
    for the same order_id + customer_id; otherwise runs the pipeline.
    """
    try:
        # 1. Cache lookup (sync DB call, so run it in a thread)
        cached = await run_in_threadpool(
            get_specific_execution, input_data.order_id, input_data.customer_id
        )
        if cached is not None:
            logger.info(
                f"CACHE HIT order={input_data.order_id} customer={input_data.customer_id}"
            )
            return build_response(cached, cached=True)

        # 2. Miss: run the pipeline (it saves the execution row itself)
        logger.info(
            f"CACHE MISS order={input_data.order_id} customer={input_data.customer_id}"
        )
        investigator = Investigator()
        result: FinalResult = await investigator.run(
            input_data=input_data,
            user_id=profile.user_id,
        )

        logger.info(
            f"Delivery Investigator finished; investigation completed: "
            f"{'True' if result.agent_result.investigation_success else 'False'}"
        )
        return build_response(result, cached=False)

    except Exception:
        logger.exception("Failed to run delivery investigator")
        raise HTTPException(
            status_code=500,
            detail="The investigation could not be completed. Please try again later.",
        )