from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from app.get_upfront_data import get_upfront_data
from schemas import UpfrontDataSchema, InputDataSchema

from api.dependencies import get_current_profile

router = APIRouter(prefix="/upfront_data", tags=["Upfront Data"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.post(
        "/get-upfront-data",
        dependencies=[Depends(get_current_profile)]
        )
@limiter.limit("50/minute")
async def endpoint_get_upfrontdata(
    request: Request, 
    input_data: InputDataSchema
    ):
    """
    Retrieves the upfront data for a given customer and order.
    """
    try:
        data: UpfrontDataSchema = get_upfront_data(
            customer_id=input_data.customer_id,
            order_id=input_data.order_id
        )

        logger.info(f"Got upfront data for order : {data.order.order_id}")

        return {
            "status": "success",
            "result": data,
        }

    except Exception:
        logger.exception("Failed to get upfront data")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve upfront data. Please try again later.",
        )