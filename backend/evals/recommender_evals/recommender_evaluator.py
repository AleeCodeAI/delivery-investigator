import json
import time
from uuid import uuid4
from pathlib import Path
from openai import OpenAI
from langfuse.decorators import observe

from schemas import RecommenderEvalsResult
from prompts.prompt_manager import PromptManager
from evals.evals_obs.recommender_evals_obs import RecommenderEvaluatorObservability
from configs.settings import get_settings
from utils.color import Logger
from .report_generator import generate_report


class RecommenderEvaluator(Logger):

    name: str = "RecommenderEvaluator"
    color: str = Logger.PINK

    CASE_DELAY_SECONDS = 5   # wait between cases (usage limit)
    RECOMMENDER_PASS_RATE = 90.0    # % of cases that must pass

    def __init__(self):
        self.settings = get_settings()
        self.prompt = PromptManager().get_recommender_evals_system_prompt()
        self.obs = RecommenderEvaluatorObservability()

        self.client = OpenAI(
            api_key=self.settings.groq.api_key,
            base_url=self.settings.groq.base_url,
        )

        data_dir = Path(__file__).parents[3] / "data"
        self.input_data_path = data_dir / "evals_data" / "recommender_evals_data.json"
        self.policy_path = data_dir / "company_policies.md"
        self.execution_path = Path(__file__).parent / "results" / "execution.json"
        self.report_path = Path(__file__).parent / "results" / "report.md"

        self.log("RecommenderEvaluator initialized successfully.")

    # ---------------------------- data ---------------------------- #
    def _load_cases(self) -> list[dict]:
        with open(self.input_data_path, encoding="utf-8") as f:
            self.log(f"Loaded cases.")
            return json.load(f)
        
    def _load_policy(self) -> str:
        with open(self.policy_path, encoding="utf-8") as f:
            return f.read()

    # ---------------------------- judge ---------------------------- #
    def _user_input(self, case: dict) -> str:
        return (
            f"COMPANY POLICY:\n\n"
            f"{self._load_policy()}\n\n"
            f"RECOMMENDER RESULT:\n\n"
            f"Recommendation:\n{case['recommendation']}\n\n"
            f"Evidences:\n{case['evidences']}\n"
        )

    def _make_messages(self, user_input: str) -> list[dict]:
        return [
            {"role": "system", "content": self.prompt.prompt},
            {"role": "user", "content": user_input},
        ]

    @observe(as_type="generation", name="Judge_LLM_Call")
    def _call_llm(self, messages: list[dict]) -> RecommenderEvalsResult:
        """Calls the judge with retries and logs the generation to Langfuse."""
        last_exception = None

        for attempt in range(1, self.settings.groq.max_retries + 1):
            try:
                response = self.client.chat.completions.parse(
                    model=self.settings.groq.default_model,
                    messages=messages,
                    temperature=self.settings.groq.temperature,
                    response_format=RecommenderEvalsResult,
                )
                result: RecommenderEvalsResult = response.choices[0].message.parsed

                self.obs.log_generation(
                    messages=messages,
                    output=result,
                    usage=response.usage,
                    model=self.settings.groq.default_model,
                    prompt=self.prompt,
                )
                return result

            except Exception as e:
                last_exception = e
                self.log(f"Judge call failed (attempt {attempt}/{self.settings.groq.max_retries}): {e}")
                if attempt < self.settings.groq.max_retries:
                    time.sleep(2)

        raise last_exception

    @observe(name="Recommender_Evaluation_Case")
    def _evaluate_single_case(self, case: dict, run_id: str) -> dict:
        case_id = case["order_id"]
        self.log(f"EVALUATING CASE: {case_id}")
        self.obs.init_eval_trace(run_id=run_id, case=case)

        try:
            user_input = self._user_input(case)
            messages = self._make_messages(user_input)
            result = self._call_llm(messages)
            self.obs.process_result(result)

            self.log(f"Score: {result.overall_score}, Passed: {result.overall_passed}")

            return {
                "case_id": case_id,
                "recommendation_correct": result.recommendation_correct,
                "evidence_consistency_correct": result.evidence_consistency_correct,
                "overall_score": result.overall_score,
                "overall_passed": result.overall_passed,
                "judge_reasoning": result.judge_reasoning,
            }

        except Exception as e:
            self.obs.process_failure(e)
            self.log(f"Error evaluating case {case_id}: {e}")

            return {
                "case_id": case_id,
                "recommendation_correct": None,
                "evidence_consistency_correct": None,
                "overall_score": 0,
                "overall_passed": False,
                "judge_reasoning": f"ERROR: {e}",
            }

    # ---------------------------- saving ---------------------------- #
    def _save_execution(self, records: list[dict]):
        self.execution_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.execution_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=4, ensure_ascii=False)
        self.log(f"Execution results saved to {self.execution_path}")

    def _save_report(self, report: str):
        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.report_path, "w", encoding="utf-8") as f:
            f.write(report)
        self.log(f"Report saved to {self.report_path}")

    # ----------------------------- main ----------------------------- #
    def evaluate(self) -> list[dict]:
        """Evaluates every case. `limit` caps the number of cases (for smoke tests)."""
        run_id = str(uuid4())
        cases = self._load_cases()
        records = []

        try:
            for i, case in enumerate(cases, start=1):
                records.append(self._evaluate_single_case(case, run_id))

                if i < len(cases):
                    time.sleep(self.CASE_DELAY_SECONDS)  # usage limit buffer
        finally:
            self._save_execution(records)  # saved even if the run is interrupted
            self.obs.flush()

        report = generate_report(
            records=records,
            run_id=run_id,
            judge_model=self.settings.groq.default_model,
            recommender_pass_rate=self.RECOMMENDER_PASS_RATE,
        )
        self._save_report(report)

        passed = sum(r["overall_passed"] for r in records)
        pass_rate = passed / len(records) * 100 if records else 0.0
        verdict = "PASSED" if pass_rate >= self.RECOMMENDER_PASS_RATE else "FAILED"
        self.log(f"{passed}/{len(records)} passed ({pass_rate:.1f}%). Recommender {verdict}.")

        return records


if __name__ == "__main__":
    RecommenderEvaluator().evaluate()