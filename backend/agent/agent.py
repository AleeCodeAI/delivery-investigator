import logging

from pydantic_ai import Agent as PydanticAgent, UsageLimits
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic import BaseModel

from langfuse.decorators import langfuse_context, observe

from configs.settings import get_settings
from utils.color import Logger
from prompts.prompt_manager import PromptManager
from schemas import AgentResult, UpfrontDataSchema
from database.repos import insert_agent_result
from observability import AgentObservability

from .customer_address_history_tool import customer_address_history_tool
from .fulfillment_evidence_tool import fulfillment_evidence_tool


logging.basicConfig(level=logging.INFO, format="%(message)s")


class InvestigationAgent(Logger):
    """
    Agent that investigates a shipment using upfront customer, order,
    shipment and shipment event data.
    It runs a pydantic-ai agent backed by an OpenRouter model, equipped with
    the customer address history and fulfillment evidence tools, and returns
    a structured AgentResult. Failures never propagate: a fallback result with
    investigation_success=False is returned instead.
    """

    name: str = "Agent"
    color: str = Logger.GREEN

    def __init__(self):
        """
        Initialize the investigation agent.
        Builds the OpenRouter-backed model and the underlying pydantic-ai agent
        with its tools, system prompt, output type and retry settings.
        """
        self.settings = get_settings()
        self.prompt = PromptManager().get_agent_system_prompt()
        self.provider = OpenAIProvider(
            base_url=self.settings.openrouter.base_url,
            api_key=self.settings.openrouter.api_key,
        )
        self.model = OpenAIChatModel(
            provider=self.provider,
            model_name=self.settings.openrouter.default_model
        )
        self.agent = PydanticAgent(
            model=self.model,
            tools=[customer_address_history_tool, fulfillment_evidence_tool],
            output_type=AgentResult,
            system_prompt=self.prompt.prompt,
            retries=self.settings.agent.max_retries,
        )
        self.obs = AgentObservability()

        self.log(f"Agent initialized successfully with model: {self.settings.openrouter.default_model}")

    @staticmethod
    def _format_data(data: BaseModel | None) -> str:
        """
        Format a Pydantic model's fields into a readable string.
        Args:
            data: The Pydantic model to format, or None.
        Returns:
            A formatted string containing the model's fields and values.
        """
        if data is None:
            return "Unavailable"

        return "\n".join(
            f"- {key.replace('_', ' ').title()}: "
            f"{value if value is not None else 'Unavailable'}"
            for key, value in data.model_dump().items()
        )

    @observe(as_type="span", name="user_input")
    def _user_input(self, upfront_data: UpfrontDataSchema, investigation_prompt: str) -> str:
        """
        Format upfront data into a structured user input for the agent.
        Args:
            upfront_data: Customer, order, shipment, and shipment event data.
            investigation_prompt: The prompt for the investigation.
        Returns:
            A formatted string containing all upfront data.
        """
        shipment_events = (
            "\n\n".join(
                self._format_data(event)
                for event in upfront_data.shipment_events
            )
            if upfront_data.shipment_events
            else "No shipment events available."
        )

        return (
            f"INVESTIGATION PROMPT\n{investigation_prompt}\n\n"
            "CUSTOMER DETAILS\n"
            f"{self._format_data(upfront_data.customer)}\n\n"
            "ORDER DETAILS\n"
            f"{self._format_data(upfront_data.order)}\n\n"
            "SHIPMENT DETAILS\n"
            f"{self._format_data(upfront_data.shipment)}\n\n"
            "SHIPMENT EVENTS\n"
            f"{shipment_events}"
        )

    @observe(as_type="generation", name="agent_generation")
    async def _agent(self, user_input: str):
        """
        Run the underlying pydantic-ai agent with the formatted input.
        Args:
            user_input: The formatted user input for the agent.
        Returns:
            The raw run result from the agent, including output and usage.
        Raises:
            Exception: Re-raises any agent failure after logging it.
        """
        try:
            result = await self.agent.run(
                user_prompt=user_input,
                usage_limits=UsageLimits(
                    request_limit=self.settings.agent.max_iterations
                )
            )

            usage = result.usage

            input_cost, output_cost, total_cost = self.obs.log_generation(
                usage=usage,
                output=result.output,
                prompt=self.prompt

            )

            self.log(
                f"Agent run completed: requests={usage.requests}, "
                f"total_tokens={usage.total_tokens}"
                f" | input_cost=${input_cost:.6f}, "
                f"output_cost=${output_cost:.6f}, total_cost=${total_cost:.6f}"
            )

            return result

        except Exception as e:
            langfuse_context.update_current_observation(level="ERROR", status_message=str(e))
            self.log(f"Agent execution failed: {e}")
            raise

    @observe()
    async def run(
                self, 
                upfront_data: UpfrontDataSchema, 
                investigation_prompt: str,
                session_id: str
            ) -> AgentResult:
        """
        Run the investigation for the provided upfront data.
        Never raises: on any failure or usage limit hit, a fallback
        AgentResult with investigation_success=False is returned.
        Args:
            upfront_data: Customer, order, shipment, and shipment event data.
            investigation_prompt: The prompt for the investigation.
            session_id: A unique identifier for the investigation session.
        Returns:
            The agent's structured result, or a fallback result on failure.
        """
        try:
            self.log(
                f"Starting agent execution for "
                f"the customer: {upfront_data.customer.name}; Order ID: {upfront_data.order.order_id}"
            )
            self.obs.init_agent_trace(
                session_id=session_id,
                customer_id=upfront_data.customer.customer_id,
                order_id=upfront_data.order.order_id,
                investigation_prompt=investigation_prompt,
                max_iterations=self.settings.agent.max_iterations
                
            )

            user_input = self._user_input(upfront_data, investigation_prompt)
            result = await self._agent(user_input)
            output: AgentResult = result.output

            self.obs.process_result(result=output)

            insert_agent_result(
                execution_id=session_id,
                agent_result=output.model_dump(mode="json")
            )

            self.log(
                f"Investigation finished: success={output.investigation_success}; "
                f"confidence={output.confidence}"
            )

            return output

        except Exception as e:
            self.log(f"Agent failed or hit usage limits: {e}")
            self.log("Returning fallback response.")

            self.obs.process_result(error=e)
            
            return None

if __name__ == "__main__":
    from app.get_upfront_data import get_upfront_data
    import asyncio
    from uuid import uuid4
    from database.repos import insert_starting_execution, insert_upfront_data

    session_id = str(uuid4())
    customer_id = "CUST-189053"
    order_id = "ORD-189053"
    investigation_prompt = "Investigate order ORD-189053. The delivery destination differs from the customer's current address. Determine what the records establish about the discrepancy."

    insert_starting_execution(
        execution_id=session_id,
        customer_id=customer_id,
        order_id=order_id,
        investigation_prompt=investigation_prompt
    )
    upfrontdata: UpfrontDataSchema = get_upfront_data(
            customer_id=customer_id,
            order_id=order_id
        )
    insert_upfront_data(
        execution_id=session_id,
        upfront_data=upfrontdata.model_dump(mode="json")
    )
    
    agent = InvestigationAgent()
    result = asyncio.run(
            agent.run(
                upfront_data=upfrontdata,
                investigation_prompt=investigation_prompt,
                session_id=session_id
            )
        )
    print(result)