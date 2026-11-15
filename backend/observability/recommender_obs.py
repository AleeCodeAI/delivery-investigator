from contextlib import contextmanager

from langfuse import Langfuse, propagate_attributes
from configs.settings import get_settings
from schemas import RecommenderResult

class RecommenderObservability:
    """Class to handle observability for the Recommender using Langfuse."""

    def __init__(self):
        self.settings = get_settings()
        self.langfuse = Langfuse(
            secret_key=self.settings.langfuse.secret_key,
            public_key=self.settings.langfuse.public_key,
            host=self.settings.langfuse.host
        )

    @contextmanager
    def init_trace(self, session_id: str, investigation_report: str):
        """Sets trace attributes for everything run inside the `with` block."""

        self.langfuse.update_current_span(
            input={"investigation_report": investigation_report}
        )

        with propagate_attributes(
            session_id=session_id,
            trace_name="Recommender_Execution",
            tags=["recommender", "Groq", "OpenRouter"],
        ):
            yield

    def log_generation(self, usage, output, prompt, model):
        """
        Logs a generation to Langfuse with token usage and cost information.

        Args:
            usage: The usage object from OpenAI SDK
            output: The output of the generation
            prompt: The Langfuse prompt object (links this generation to the prompt version)
            model: the model used for generation
        """
        # Safely extract input/output tokens handling both OpenAI SDK and Pydantic-AI formats
        input_tokens = getattr(usage, "prompt_tokens", None) or getattr(usage, "input_tokens", 0)
        output_tokens = getattr(usage, "completion_tokens", None) or getattr(usage, "output_tokens", 0)
        total_tokens = getattr(usage, "total_tokens", input_tokens + output_tokens)

        # Calculate costs
        input_cost = (input_tokens / 1_000_000) * self.settings.openrouter.GPT_OSS_INPUT_PRICE
        output_cost = (output_tokens / 1_000_000) * self.settings.openrouter.GPT_OSS_OUTPUT_PRICE
        total_cost = round(input_cost + output_cost, 6)

        self.langfuse.update_current_generation(
            output=output,
            prompt=prompt,
            model=model,
            usage_details={
                "input": input_tokens,
                "output": output_tokens,
                "total": total_tokens,
            },
            cost_details={
                "input": input_cost,
                "output": output_cost,
                "total": total_cost,
            },
        )

        return total_cost

    def process_result(self, result: RecommenderResult):
        """Logs the final output and dynamically scores it."""

        self.langfuse.update_current_span(output=result.model_dump())

        success = result.recommendation is not None and result.recommendation != ""
        self.langfuse.create_score(
            name="recommendation-success",
            value=1 if success else 0,
            trace_id=self.langfuse.get_current_trace_id(),
            comment=(
                "Recommendation Generated Successfully!"
                if success
                else "Recommender couldn't generate!"
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
            name="recommendation-success",
            value=0,
            trace_id=self.langfuse.get_current_trace_id(),
            comment=f"Recommender crashed/failed: {error_msg}",
        )

    def flush(self):
        self.langfuse.flush()