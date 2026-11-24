from sqlalchemy import select
from sqlalchemy.orm import Session
from database.engine import engine
from database.models import Execution
from schemas import ExecutionSchema, FinalResult, UpfrontDataSchema
from datetime import datetime, timedelta, timezone
from uuid import UUID

CACHE_TTL = timedelta(hours=1) 


def get_executions_by_user_id(user_id: UUID):
    """
    Retrieve all executions associated with a specific user.

    Args:
        user_id (UUID): The unique identifier of the user.

    Returns:
        List[ExecutionSchema]: A list of execution instances associated with the user.
    """
    with Session(engine) as session:
        stmt = select(Execution).where(Execution.user_id == user_id)
        execution_rows = session.execute(stmt).scalars().all()

        return [
            ExecutionSchema(
                execution_id=execution.execution_id,
                user_id=execution.user_id,
                customer_id=execution.customer_id,
                order_id=execution.order_id,
                investigation_prompt=execution.investigation_prompt,
                upfront_data=execution.upfront_data,
                agent_result=execution.agent_result,
                recommender_result=execution.recommender_result,
                execution_success=execution.execution_success,
                execution_date=execution.execution_date,
                error_message=execution.error_message
            )
            for execution in execution_rows
        ]


def get_all_executions():
    """
    Retrieve all executions from the database.

    Returns:
        List[ExecutionSchema]: A list of all execution instances.
    """
    with Session(engine) as session:
        stmt = select(Execution)
        execution_rows = session.scalars(stmt).all()
        
        return [
            ExecutionSchema(
                execution_id=execution.execution_id,
                user_id=execution.user_id,
                customer_id=execution.customer_id,
                order_id=execution.order_id,
                investigation_prompt=execution.investigation_prompt,
                upfront_data=execution.upfront_data,
                agent_result=execution.agent_result,
                recommender_result=execution.recommender_result,
                execution_success=execution.execution_success,
                execution_date=execution.execution_date,
                error_message=execution.error_message
            )
            for execution in execution_rows
        ]
    

def get_specific_execution(order_id: str, customer_id: str):
    """
    Return (FinalResult, UpfrontDataSchema) for the most recent successful
    execution within the cache TTL, or None on a cache miss.
    """
    cutoff = datetime.now(timezone.utc) - CACHE_TTL

    with Session(engine) as session:
        stmt = (
            select(Execution)
            .where(
                Execution.order_id == order_id,
                Execution.customer_id == customer_id,
                Execution.execution_success.is_(True),
                Execution.execution_date >= cutoff,
            )
            .order_by(Execution.execution_date.desc())
            .limit(1)
        )
        execution = session.scalars(stmt).first()

        if execution is None:
            return None

        final_result = FinalResult(
            agent_result=execution.agent_result,
            recommender_result=execution.recommender_result,
        )

        return final_result


if __name__ == "__main__":
    try:
        result = get_specific_execution(order_id="ORD-189053", customer_id="CUST-189053")
        print(result)
    except LookupError as e:
        print(e)