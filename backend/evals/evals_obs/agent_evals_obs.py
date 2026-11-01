from langfuse.decorators import langfuse_context

from configs.settings import get_settings
from schemas import AgentEvalsResult


class AgentEvaluatorObservability:
    """Handles Langfuse observability for the Agent Evaluator."""

    def __init__(self):
        self.settings = get_settings()
        # The decorators use this global context, so configure it with our keys
        langfuse_context.configure(
            secret_key=self.settings.langfuse.secret_key,
            public_key=self.settings.langfuse.public_key,
            host=self.settings.langfuse.host,
        )

    def init_eval_trace(self, run_id: str, case: dict):
        """Initializes the trace when evaluating a single case. Cases of one run share a session."""
        langfuse_context.update_current_trace(
            session_id=run_id,
            name="Agent_Evaluation_Case",
            tags=["evaluator", "groq", "delivery-investigator"],
            input={
                "input_id": case["input_id"],
                "order_id": case["order_id"],
                "problem_description": case["problem_description"],
            },
            metadata={"scenario_subtype": case["scenario_subtype"]},
        )

    def log_execution_id(self, execution_id: str):
        """Links this eval trace to the agent execution it judged."""
        langfuse_context.update_current_trace(metadata={"execution_id": execution_id})

    def log_generation(self, messages: list, output: AgentEvalsResult, usage, model: str, prompt):
        """Logs the judge generation payload and token usage."""
        langfuse_context.update_current_observation(
            input=messages,
            prompt=prompt,
            output=output.model_dump(),
            model=model,
            usage={
                "input": usage.prompt_tokens if usage else 0,
                "output": usage.completion_tokens if usage else 0,
                "total": usage.total_tokens if usage else 0,
                "unit": "TOKENS",
            },
        )

    def process_result(self, result: AgentEvalsResult):
        """Logs the final result and scores each criterion plus the overall result."""
        langfuse_context.update_current_trace(output=result.model_dump())

        criteria = {
            "cause-correct": result.cause_correct,
            "evidence-identification-correct": result.evidence_identification_correct,
            "evidence-consistency-correct": result.evidence_consistency_correct,
        }
        for name, value in criteria.items():
            langfuse_context.score_current_trace(name=name, value=1 if value else 0)

        langfuse_context.score_current_trace(
            name="overall-score",
            value=result.overall_score,
            comment=result.judge_reasoning,
        )
        langfuse_context.score_current_trace(
            name="overall-passed",
            value=1 if result.overall_passed else 0,
            comment=f"Score: {result.overall_score}",
        )

    def process_failure(self, error: Exception):
        """Logs exceptions and scores the trace as a failure."""
        error_msg = str(error)
        langfuse_context.update_current_observation(level="ERROR", status_message=error_msg)
        langfuse_context.update_current_trace(
            metadata={"error_type": type(error).__name__, "error_details": error_msg}
        )
        langfuse_context.score_current_trace(
            name="overall-passed",
            value=0,
            comment=f"Evaluator pipeline crashed: {error_msg}",
        )

    def flush(self):
        langfuse_context.flush()