from langfuse import Langfuse
from langfuse.decorators import langfuse_context
from configs.settings import get_settings
from schemas import AgentResult

class AgentObservability:
    """Class to handle observability for the Agent using Langfuse."""

    def __init__(self):
        self.settings = get_settings()
        self.langfuse = Langfuse(
            secret_key=self.settings.langfuse.secret_key,
            public_key=self.settings.langfuse.public_key,
            host=self.settings.langfuse.host
        )

    def init_agent_trace(
            self, 
            session_id: str, 
            customer_id: str, 
            order_id: str,
            investigation_prompt: str,
            max_iterations: int
            ):
        """Initializes the trace metadata when the agent run starts."""

        langfuse_context.update_current_trace(
            session_id=session_id,
            name="InvestigationAgent_Execution",
            tags=["investigation-agent", "pydantic-ai"],
            input={"investigation_prompt": investigation_prompt},
            metadata={
                "max_iterations": max_iterations,
                "customer_id": customer_id,
                "order_id": order_id
            }
        )

    def log_generation(self, usage, output, prompt):
        """
        Logs a generation to Langfuse with token usage and cost information.

        Args:
            usage: The usage object from pydantic-ai
            output: The output of the generation
            prompt: The prompt used for the generation
        """

        input_cost = (usage.input_tokens / 1_000_000) * self.settings.openrouter.GPT_OSS_INPUT_PRICE
        output_cost = (usage.output_tokens / 1_000_000) * self.settings.openrouter.GPT_OSS_OUTPUT_PRICE
        total_cost = round(input_cost + output_cost, 6)

        langfuse_context.update_current_observation(
            output=output,
            prompt=prompt,
            model=self.settings.openrouter.default_model,
            usage={
                "input": usage.input_tokens,
                "output": usage.output_tokens,
                "total": usage.total_tokens,
                "unit": "TOKENS",
                "inputCost": input_cost,
                "outputCost": output_cost,
                "totalCost": total_cost,
            },
            metadata={
                "requests": getattr(usage, "requests", None),
                "max_iterations": self.settings.agent.max_iterations
                },
        )

        return input_cost, output_cost, total_cost

    def process_result(self, result: AgentResult):
        """Logs the final Pydantic model as output and dynamically scores it."""

        langfuse_context.update_current_trace(output=result.model_dump())

        if result.investigation_success:
            langfuse_context.score_current_trace(
                name="investigation-success",
                value=1,
                comment=f"Investigation completed successfully. Confidence: {result.confidence}"
            )
        else:
            langfuse_context.score_current_trace(
                name="investigation-success",
                value=0,
                comment=f"Investigation failed. Confidence: {result.confidence}"
            )

    def process_failure(self, error: Exception):
        """Logs exceptions and scores the trace as a failure."""
        error_msg = str(error)
        
        langfuse_context.update_current_observation(
            level="ERROR", 
            status_message=error_msg
        )
        langfuse_context.update_current_trace(
            metadata={"error_type": type(error).__name__, "error_details": error_msg}
        )

        langfuse_context.score_current_trace(
            name="investigation-success",
            value=0,
            comment=f"Agent crashed/failed: {error_msg}"
        )

    def flush(self):
        self.langfuse.flush()