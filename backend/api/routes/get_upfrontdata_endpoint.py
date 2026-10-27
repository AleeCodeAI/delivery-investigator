from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from app.get_upfront_data import get_upfront_data
from schemas import UpfrontDataSchema, InputDataSchema

router = APIRouter(prefix="/upfront_data", tags=["Upfront Data"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.post("/get-upfront-data")
@limiter.limit("50/minute")
async def endpoint_get_history(request: Request, input_data: InputDataSchema):
    """
    Retrieves all search history.
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

    except Exception as e:
        logger.exception("Failed to get histories")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get histories: {str(e)}",
        )