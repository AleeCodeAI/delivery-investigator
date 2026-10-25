import logging
from uuid import uuid4
from typing import Optional

from utils.color import Logger
from agent.agent import InvestigationAgent
from .recommender import Recommender
from .get_upfront_data import get_upfront_data
from schemas import (
    FinalResult,
    AgentResult,
    RecommenderResult,
    UpfrontDataSchema,
    InputDataSchema
    )
from database.repos import (
    insert_starting_execution,
    insert_upfront_data,
    mark_execution_failure,
    mark_execution_success
    )


logging.basicConfig(level=logging.INFO, format="%(message)s")


class Investigator(Logger):
    """
    Orchestrates the investigation pipeline for a customer order.

    This class serves as the primary coordinator. It records the execution,
    gathers the upfront customer and order data, passes it to the Agent to
    run the investigation, and then forwards the findings to the Recommender
    to produce the final recommendations.

    Attributes:
        name (str): The identifier for this class, used primarily for logging.
        color (str): The color constant applied to console logs for this class.
    """

    name: str = "Investigator"
    color: str = Logger.MAGENTA

    def __init__(self):
        """
        Initializes the Investigator along with its required components.

        Raises:
            Exception: Any error raised while initializing the Agent or the
                Recommender, after it has been logged.
        """
        try:
            self.log("Initializing the Investigator...")

            self.agent = InvestigationAgent()
            self.recommender = Recommender()

            self.log("Initialized the Investigator")

        except Exception as e:
            self.log(f"Failed to initialize the Investigator: {str(e)}")
            raise

    async def run(self, input_data: InputDataSchema) -> FinalResult:
        """
        Executes the end-to-end investigation for a customer order.

        Generates a unique session ID to track the investigation through the
        pipeline and persists its status in the database. The upfront data and
        the agent result are required; if either is missing the run fails.
        The recommender result is optional, so the run continues without it.

        Args:
            input_data (InputDataSchema): The customer ID, order ID and
                investigation prompt describing what to investigate.

        Returns:
            FinalResult: A structured object containing the agent result and
                the recommender result, which is None if the recommender
                failed.

        Raises:
            ValueError: If the upfront data or the agent result is missing,
                after the execution has been marked as failed.
            Exception: Any other error raised by the pipeline, after the
                execution has been marked as failed.
        """
        session_id = str(uuid4())

        insert_starting_execution(
            execution_id=session_id,
            customer_id=input_data.customer_id,
            order_id=input_data.order_id,
            investigation_prompt=input_data.investigation_prompt
        )

        try:
            self.log(
                f"Starting investigation \n"
                f"[Session: {session_id}] \n"
                f"[Customer: {input_data.customer_id}] \n"
                f"[Order: {input_data.order_id}]"
            )

            upfront_data: Optional[UpfrontDataSchema] = get_upfront_data(
                customer_id=input_data.customer_id,
                order_id=input_data.order_id
            )

            if upfront_data is None:
                raise ValueError(
                    "The investigator couldn't get upfront data to proceed"
                )

            insert_upfront_data(
                execution_id=session_id,
                upfront_data=upfront_data.model_dump(mode="json")
            )

            self.log(f"Upfront data stored [Session: {session_id}]")

            self.log(f"Running the agent [Session: {session_id}]")

            agent_result: Optional[AgentResult] = await self.agent.run(
                session_id=session_id,
                investigation_prompt=input_data.investigation_prompt,
                upfront_data=upfront_data
            )

            if agent_result is None:
                raise ValueError(
                    "The agent couldn't return investigation result to proceed"
                )

            self.log(f"Generating recommendations [Session: {session_id}]")

            recommender_result: Optional[RecommenderResult] = (
                self.recommender.recommend(
                    session_id=session_id,
                    agent_result=agent_result
                )
            )

            if recommender_result is None:
                self.log(
                    f"Recommender returned no result, continuing without "
                    f"recommendations [Session: {session_id}]"
                )

            final_result: FinalResult = FinalResult(
                agent_result=agent_result,
                recommender_result=recommender_result
            )

            mark_execution_success(execution_id=session_id)

            self.log(f"Investigation completed [Session: {session_id}]")

            return final_result

        except Exception as e:

            mark_execution_failure(
                execution_id=session_id,
                error_message=str(e)
            )

            self.log(
                f"Pipeline failed for session "
                f"{session_id}: {str(e)}"
            )

            raise

if __name__ == "__main__":
    import asyncio

    investigator = Investigator()
    input_data = InputDataSchema(
        customer_id="CUST-189053",
        order_id="ORD-189053",
        investigation_prompt="Investigate order ORD-189053. The delivery destination differs from the customer's current address. Determine what the records establish about the discrepancy."
    )
    result = asyncio.run(
        investigator.run(input_data=input_data)
    )
    print(result.agent_result)
    print("---------------------")
    print(result.recommender_result)