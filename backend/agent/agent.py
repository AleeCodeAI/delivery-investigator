import logging

from pydantic_ai import Agent as PydanticAgent, UsageLimits
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic import BaseModel

from configs.settings import get_settings
from utils.color import Logger
from prompts.prompt_manager import PromptManager
from schemas import AgentResult, UpfrontDataSchema

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
            self.log(
                f"Agent run completed: requests={usage.requests}, "
                f"total_tokens={usage.total_tokens}"
            )

            return result

        except Exception as e:
            self.log(f"Agent execution failed: {e}")
            raise

    async def run(self, upfront_data: UpfrontDataSchema, investigation_prompt: str) -> AgentResult:
        """
        Run the investigation for the provided upfront data.
        Never raises: on any failure or usage limit hit, a fallback
        AgentResult with investigation_success=False is returned.
        Args:
            upfront_data: Customer, order, shipment, and shipment event data.
            investigation_prompt: The prompt for the investigation.
        Returns:
            The agent's structured result, or a fallback result on failure.
        """
        try:
            self.log(
                f"Starting agent execution for "
                f"the customer: {upfront_data.customer.name}; Order ID: {upfront_data.order.order_id}"
            )

            user_input = self._user_input(upfront_data, investigation_prompt)
            result = await self._agent(user_input)
            output: AgentResult = result.output

            self.log(
                f"Investigation finished: success={output.investigation_success}; "
                f"confidence={output.confidence}"
            )

            return output

        except Exception as e:
            self.log(f"Agent failed or hit usage limits: {e}")
            self.log("Returning fallback response.")

            return AgentResult(
                investigation_report=f"The agent failed to complete the investigation with error: {e}",
                evidences=[],
                investigation_success=False,
                confidence=0.0
            )

if __name__ == "__main__":
    from app.get_upfront_data import get_upfront_data
    import asyncio

    upfrontdata: UpfrontDataSchema = get_upfront_data(
            customer_id="CUST-189053",
            order_id="ORD-189053"
        )
    agent = InvestigationAgent()
    result = asyncio.run(
            agent.run(
                upfront_data=upfrontdata,
                investigation_prompt="Investigate order ORD-189053. The delivery destination differs from the customer's current address. Determine what the records establish about the discrepancy."
            )
        )
    print(result)