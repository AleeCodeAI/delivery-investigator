from pathlib import Path

from langfuse.decorators import observe
from openai import OpenAI

from configs.settings import get_settings
from database.repos import insert_recommender_result
from observability import RecommenderObservability
from prompts.prompt_manager import PromptManager
from schemas import AgentResult, RecommenderResult
from utils.color import Logger


class Recommender(Logger):
    """
    Turn a delivery investigation result into a policy-based recommendation.

    Builds a prompt from the investigation report, its evidences, and the
    company policies, calls an LLM with provider fallback, stores the result,
    and records observability data. It only recommends; a human operator acts.
    """

    name: str = "Recommender"
    color: str = Logger.BLUE

    def __init__(self):
        """
        Initialize settings, prompt, LLM clients, and observability context.
        """
        self.log("Initializing Recommender...")

        self.settings = get_settings()
        self.prompt = PromptManager().get_recommender_system_prompt()

        self.openrouter = OpenAI(
            api_key=self.settings.openrouter.api_key,
            base_url=self.settings.openrouter.base_url,
        )
        self.groq = OpenAI(
            api_key=self.settings.groq.api_key,
            base_url=self.settings.groq.base_url,
        )

        self.gpt_oss_model = self.settings.openrouter.default_model
        self.obs = RecommenderObservability()
        self.company_policies_path = (
            Path(__file__).parents[2] / "data" / "company_policies.md"
        )

        self.log("Recommender initialized")

    def _load_company_policies(self) -> str:
        """
        Read the company policies document from disk.

        Returns:
            The full text of the company policies file.
        """
        with open(self.company_policies_path, "r", encoding="utf-8") as f:
            return f.read()

    @observe(name="prompt_formatting", as_type="span")
    def _user_prompt(self, agent_result: AgentResult, company_policy: str) -> str:
        """
        Format the user prompt from the investigation result and policies.

        Args:
            agent_result: Result of the delivery investigation.
            company_policy: Text of the company policies.

        Returns:
            The formatted user prompt.
        """
        return (
            "INVESTIGATION REPORT:\n"
            f"{agent_result.investigation_report}\n\n"
            "INVESTIGATION EVIDENCES:\n"
            f"{agent_result.evidences}\n\n\n"
            "COMPANY POLICIES:\n"
            f"{company_policy}"
        )

    @observe(name="construct_messages", as_type="span")
    def _make_messages(self, user_prompt: str) -> list[dict]:
        """
        Build the chat messages for the LLM request.

        Args:
            user_prompt: The formatted user prompt.

        Returns:
            A list with the system message followed by the user message.
        """
        return [
            {"role": "system", "content": self.prompt.prompt},
            {"role": "user", "content": user_prompt},
        ]

    @observe(name="synthesizer_generation", as_type="generation")
    def _call_llm(self, messages: list[dict]) -> RecommenderResult:
        """
        Call the LLM providers in order and return the first successful result.

        Args:
            messages: Chat messages to send to the model.

        Returns:
            The parsed recommendation.

        Raises:
            Exception: The last provider error if all providers fail.
        """
        self.log("Calling LLM providers for recommendations...")

        providers = [
            ("Groq", self.groq, self.gpt_oss_model),
            ("OpenRouter", self.openrouter, self.gpt_oss_model),
        ]

        last_error = None

        for provider_name, client, model in providers:
            try:
                self.log(f"Trying LLM provider: {provider_name}")

                raw = client.chat.completions.parse(
                    model=model,
                    messages=messages,
                    response_format=RecommenderResult,
                    temperature=0.3,
                )

                result = raw.choices[0].message.parsed
                if result is None:
                    raise ValueError("Model returned no parsed result")

                total_cost = None
                if getattr(raw, "usage", None):
                    total_cost = self.obs.log_generation(
                        usage=raw.usage,
                        output=result.model_dump(),
                        prompt=self.prompt,
                        model=model,
                    )

                self.log(f"Recommendation successfully generated with total cost: {total_cost}")
                return result

            except Exception as e:
                last_error = e
                self.log(f"{provider_name} failed: {e}")

        self.log("All LLM providers failed")
        raise last_error

    @observe(name="Recommender_Execution")
    def recommend(self, session_id: str, agent_result: AgentResult) -> RecommenderResult:
        """
        Generate, store, and return a recommendation for an investigation result.

        Args:
            session_id: Identifier of the investigation session.
            agent_result: Result of the delivery investigation.

        Returns:
            The recommendation, or a zero-confidence fallback result if
            anything fails.
        """
        try:
            self.obs.init_trace(
                session_id=session_id,
                investigation_report=agent_result.investigation_report,
            )

            policies = self._load_company_policies()

            user_prompt = self._user_prompt(
                agent_result=agent_result,
                company_policy=policies,
            )

            messages = self._make_messages(user_prompt=user_prompt)

            result: RecommenderResult = self._call_llm(messages=messages)

            insert_recommender_result(
                execution_id=session_id,
                recommender_result=result.model_dump(mode="json"),
            )

            self.obs.process_result(result=result)

            return result

        except Exception as e:
            self.log(f"Recommender failed with error: {e}")
            self.obs.process_failure(error=e)

            return RecommenderResult(
                recommendation="recommender failed",
                evidences=[],
                confidence=0.0,
            )


if __name__ == "__main__":
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

    case = AgentResult(
        investigation_report=(
            "Finding: The order's delivery address (2568 Harbor Dr, Oakland, CA 94609) differs from the customer's current address (3364 Pine St, Los Angeles, CA 90025). The delivery address matches a historical address that was in effect for the customer from 2024-12-28 until 2026-07-09, i.e., before the order date (2026-09-03). No records indicate why the older address was used for this order. \nNot found: No evidence explaining the reason for selecting the historical address (e.g., a customer change request, system fallback, or error). No evidence of carrier misdelivery or address correction after shipment."
        ),
        evidences=[
            "[upfront] order ORD-189053, delivery address: 2568 Harbor Dr, Oakland, CA 94609", 
            "[upfront] customer CUST-189053, current address: 3364 Pine St, Los Angeles, CA 90025", "[tool:customer_address_history_tool] address history ADDR-189067, effective 2024-12-28 to 2026-07-09: 2568 Harbor Dr, Oakland, CA 94609", 
            "[tool:customer_address_history_tool] address history ADDR-189068, effective from 2026-07-10 onward: 3364 Pine St, Los Angeles, CA 90025"
        ],
        investigation_success=True,
        confidence=0.85,
    )

    result = Recommender().recommend(
        session_id=f"test-{session_id}",
        agent_result=case,
    )

    print(f"Recommendation: {result.recommendation}")
    print(f"Evidences: {result.evidences}")
    print(f"Confidence: {result.confidence}")