import json
import time
from pathlib import Path
from uuid import uuid4

from langfuse.decorators import observe
from openai import OpenAI

from configs.settings import get_settings
from prompts.prompt_manager import PromptManager
from evals.evals_obs.agent_evals_obs import AgentEvaluatorObservability
from .report_generator import generate_report
from schemas import AgentEvalsResult
from utils.color import Logger


class AgentEvaluator(Logger):
    """Grades the saved investigation agent outputs against the ground truth with an LLM judge."""

    name: str = "AgentEvaluator"
    color: str = Logger.CYAN

    CASE_DELAY_SECONDS = 10   # wait between cases (usage limit)
    AGENT_PASS_RATE = 90.0    # % of cases that must pass

    def __init__(self):
        self.settings = get_settings()
        self.prompt = PromptManager().get_agent_evals_system_prompt()
        self.obs = AgentEvaluatorObservability()

        self.client = OpenAI(
            api_key=self.settings.groq.api_key,
            base_url=self.settings.groq.base_url,
        )

        data_dir = Path(__file__).parents[3] / "data" / "evals_data"
        self.input_data_path = data_dir / "agent_evals_data.json"
        self.ground_truth_path = data_dir / "ground_truth.json"
        self.execution_path = Path(__file__).parent / "results" / "execution.json"
        self.report_path = Path(__file__).parent / "results" / "report.md"

        self.log("AgentEvaluator initialized successfully.")

    # ---------------------------- data ---------------------------- #
    @staticmethod
    def _load_json(path: Path) -> list[dict]:
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def _load_cases(self) -> list[dict]:
        """Joins each saved agent result with its ground truth on order_id."""
        ground_truth = {gt["order_id"]: gt for gt in self._load_json(self.ground_truth_path)}
        cases = [
            {**case, **ground_truth[case["order_id"]]}
            for case in self._load_json(self.input_data_path)
        ]
        self.log(f"Loaded {len(cases)} cases.")
        return cases

    # ---------------------------- judge ---------------------------- #
    @staticmethod
    def _user_input(agent_result: dict, ground_truth: dict) -> str:
        return (
            f"AGENT RESULT\n\n"
            f"Investigation Report:\n{agent_result['investigation_report']}\n\n"
            f"Evidences:\n{agent_result['evidences']}\n\n"
            f"GROUND TRUTH\n\n"
            f"Actual Scenario:\n{ground_truth['actual_scenario']}\n\n"
            f"Supporting Evidence:\n{ground_truth['supporting_evidence']}\n"
        )

    def _make_messages(self, user_input: str) -> list[dict]:
        return [
            {"role": "system", "content": self.prompt.prompt},
            {"role": "user", "content": user_input},
        ]

    @observe(as_type="generation", name="Judge_LLM_Call")
    def _call_llm(self, messages: list[dict]) -> AgentEvalsResult:
        """Calls the judge with retries and logs the generation to Langfuse."""
        last_exception = None

        for attempt in range(1, self.settings.groq.max_retries + 1):
            try:
                response = self.client.chat.completions.parse(
                    model=self.settings.groq.default_model,
                    messages=messages,
                    temperature=self.settings.groq.temperature,
                    response_format=AgentEvalsResult,
                )
                result: AgentEvalsResult = response.choices[0].message.parsed

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

    # ------------------------- single case ------------------------- #
    @observe(name="Agent_Evaluation_Case")
    def _evaluate_single_case(self, case: dict, run_id: str) -> dict:
        case_id = case["order_id"]
        self.log(f"EVALUATING CASE: {case_id}")
        self.obs.init_eval_trace(run_id=run_id, case=case)

        try:
            user_input = self._user_input(case["agent_result"], case)
            messages = self._make_messages(user_input)
            result = self._call_llm(messages)
            self.obs.process_result(result)

            self.log(f"Score: {result.overall_score}, Passed: {result.overall_passed}")

            return {
                "case_id": case_id,
                "cause_correct": result.cause_correct,
                "evidence_identification_correct": result.evidence_identification_correct,
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
                "cause_correct": None,
                "evidence_identification_correct": None,
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
    def evaluate(self, limit: int | None = None) -> list[dict]:
        """Evaluates every case. `limit` caps the number of cases (for smoke tests)."""
        run_id = str(uuid4())
        cases = self._load_cases()[:limit]
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
            records,
            run_id=run_id,
            judge_model=self.settings.groq.default_model,
            agent_pass_rate=self.AGENT_PASS_RATE,
        )
        self._save_report(report)

        passed = sum(r["overall_passed"] for r in records)
        pass_rate = passed / len(records) * 100 if records else 0.0
        verdict = "PASSED" if pass_rate >= self.AGENT_PASS_RATE else "FAILED"
        self.log(f"{passed}/{len(records)} passed ({pass_rate:.1f}%). Agent {verdict}.")

        return records


if __name__ == "__main__":
    AgentEvaluator().evaluate()