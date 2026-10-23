from database.models import Execution 
from sqlalchemy.orm import Session
from database.engine import engine 
from sqlalchemy import update


def insert_starting_execution(
                    execution_id: str, 
                    customer_id: str, 
                    order_id: str, 
                    investigation_prompt: str
                ) -> None:
    """
    Insert a new execution record into the database.

    Args:
        execution_id: The unique ID for the execution.
        customer_id: The unique ID of the customer.
        order_id: The unique ID of the order.
        investigation_prompt: The prompt used for the investigation.

    Raises:
        Exception: If there is an error during the insertion process.
    """
    with Session(engine) as session:
        try:
            new_execution = Execution(
                execution_id=execution_id,
                customer_id=customer_id,
                order_id=order_id,
                investigation_prompt=investigation_prompt
            )
            session.add(new_execution)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

def insert_upfront_data(execution_id: str, upfront_data: dict) -> None:
    """
    Update the upfront_data field of an existing execution record.

    Args:
        execution_id: The unique ID of the execution to update.
        upfront_data: A dictionary containing the upfront data to insert.

    Raises:
        Exception: If there is an error during the update process.
    """
    with Session(engine) as session:
        try:
            stmt = (
                update(Execution)
                .where(Execution.execution_id == execution_id)
                .values(upfront_data=upfront_data)
            )
            session.execute(stmt)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

def insert_agent_result(execution_id: str, agent_result: dict) -> None:
    """
    Update the agent_result field of an existing execution record.

    Args:
        execution_id: The unique ID of the execution to update.
        agent_result: A dictionary containing the agent result data to insert.

    Raises:
        Exception: If there is an error during the update process.
    """
    with Session(engine) as session:
        try:
            stmt = (
                update(Execution)
                .where(Execution.execution_id == execution_id)
                .values(agent_result=agent_result)
            )
            session.execute(stmt)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

def insert_recommender_result(execution_id: str, recommender_result: dict) -> None:
    """
    Update the recommender_result field of an existing execution record.

    Args:
        execution_id: The unique ID of the execution to update.
        recommender_result: A dictionary containing the recommender result data to insert.

    Raises:
        Exception: If there is an error during the update process.
    """
    with Session(engine) as session:
        try:
            stmt = (
                update(Execution)
                .where(Execution.execution_id == execution_id)
                .values(recommender_result=recommender_result)
            )
            session.execute(stmt)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

def mark_execution_success(execution_id: str) -> None:
    """
    Update the execution_success field of an existing execution record as True.

    Args:
        execution_id: The unique ID of the execution to update.

    Raises:
        Exception: If there is an error during the update process.
    """
    with Session(engine) as session:
        try:
            stmt = (
                update(Execution)
                .where(Execution.execution_id == execution_id)
                .values(execution_success=True)
            )
            session.execute(stmt)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

def mark_execution_failure(execution_id: str, error_message: str) -> None:
    """
    Update the execution_success field of an existing execution record as False
    and set the error_message.

    Args:
        execution_id: The unique ID of the execution to update.
        error_message: The error message to record for the failed execution.

    Raises:
        Exception: If there is an error during the update process.
    """
    with Session(engine) as session:
        try:
            stmt = (
                update(Execution)
                .where(Execution.execution_id == execution_id)
                .values(execution_success=False, error_message=error_message)
            )
            session.execute(stmt)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e