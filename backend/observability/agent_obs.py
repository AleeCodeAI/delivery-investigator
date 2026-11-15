from contextlib import contextmanager

from langfuse import Langfuse, propagate_attributes
from configs.settings import get_settings
from schemas import AgentResult


class AgentObservability:
    """Class to handle observability for the Agent using Langfuse."""

    def __init__(self):
        self.settings = get_settings()
        self.langfuse = Langfuse(
            secret_key=self.settings.langfuse.secret_key,
            public_key=self.settings.langfuse.public_key,
            host=self.settings.langfuse.host,
        )

    @contextmanager
    def init_agent_trace(
        self,
        session_id: str,
        customer_id: str,
        order_id: str,
        investigation_prompt: str,
        max_iterations: int,
    ):
        """Sets trace attributes for everything run inside the `with` block."""

        self.langfuse.update_current_span(
            input={"investigation_prompt": investigation_prompt}
        )

        with propagate_attributes(
            session_id=session_id,
            trace_name="InvestigationAgent_Execution",
            tags=["investigation-agent", "pydantic-ai"],
            metadata={
                "max_iterations": str(max_iterations),
                "customer_id": str(customer_id),
                "order_id": str(order_id),
            },
        ):
            yield

    def log_generation(self, usage, output, prompt):
        """
        Logs a generation to Langfuse with token usage and cost information.

        Args:
            usage: The usage object from pydantic-ai
            output: The output of the generation
            prompt: The Langfuse prompt object (links this generation to the prompt version)
        """

        input_cost = (usage.input_tokens / 1_000_000) * self.settings.openrouter.GPT_OSS_INPUT_PRICE
        output_cost = (usage.output_tokens / 1_000_000) * self.settings.openrouter.GPT_OSS_OUTPUT_PRICE
        total_cost = round(input_cost + output_cost, 6)

        self.langfuse.update_current_generation(
            output=output,
            prompt=prompt,
            model=self.settings.openrouter.default_model,
            usage_details={
                "input": usage.input_tokens,
                "output": usage.output_tokens,
                "total": usage.total_tokens,
            },
            cost_details={
                "input": input_cost,
                "output": output_cost,
                "total": total_cost,
            },
            metadata={
                "requests": getattr(usage, "requests", None),
                "max_iterations": self.settings.agent.max_iterations,
            },
        )

        return input_cost, output_cost, total_cost

    def process_result(self, result: AgentResult):
        """Logs the final Pydantic model as output and dynamically scores it."""

        self.langfuse.update_current_span(output=result.model_dump())

        success = result.investigation_success
        self.langfuse.create_score(
            name="investigation-success",
            value=1 if success else 0,
            trace_id=self.langfuse.get_current_trace_id(),
            comment=(
                f"Investigation completed successfully. Confidence: {result.confidence}"
                if success
                else f"Investigation failed. Confidence: {result.confidence}"
            ),
        )

    def process_failure(self, error: Exception):
        """Logs exceptions and scores the trace as a failure."""
        error_msg = str(error)

        self.langfuse.update_current_span(
            level="ERROR",
            status_message=error_msg,
            metadata={"error_type": type(error).__name__, "error_details": error_msg},
        )

        self.langfuse.create_score(
            name="investigation-success",
            value=0,
            trace_id=self.langfuse.get_current_trace_id(),
            comment=f"Agent crashed/failed: {error_msg}",
        )

    def flush(self):
        self.langfuse.flush()