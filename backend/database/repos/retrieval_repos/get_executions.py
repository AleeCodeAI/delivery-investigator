from sqlalchemy import select
from sqlalchemy.orm import Session
from database.engine import engine
from database.models import Execution
from schemas import ExecutionSchema
from uuid import UUID


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

        if execution_rows is None:
            return []
        
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

        if execution_rows is None:
            return []
        
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


if __name__ == "__main__":
    test_user_id = UUID("8fb012f3-bc02-4306-86e2-0369de5f6982")  
    try:
        executions = get_executions_by_user_id(user_id=test_user_id)
        for execution in executions:
            print(execution)
    except LookupError as e:
        print(e)