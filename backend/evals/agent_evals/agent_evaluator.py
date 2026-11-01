import asyncio
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from langfuse.decorators import observe
from openai import OpenAI

from agent.agent import InvestigationAgent
from app.get_upfront_data import get_upfront_data
from configs.settings import get_settings
from database.repos import insert_starting_execution, insert_upfront_data
from prompts.prompt_manager import PromptManager
from evals.evals_obs.agent_evals_obs import AgentEvaluatorObservability
from .report_generator import CRITERIA, generate_report
from schemas import AgentEvalsResult, AgentResult
from utils.color import Logger


class AgentEvaluator(Logger):
    """Runs the investigation agent on every eval case and grades it with an LLM judge."""

    name: str = "AgentEvaluator"
    color: str = Logger.CYAN

    CASE_DELAY_SECONDS = 10   # wait between cases (usage limit)
    AGENT_PASS_RATE = 90.0    # % of cases that must pass

    def __init__(self):
        self.settings = get_settings()
        self.agent = InvestigationAgent()
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
        """Joins each input case with its ground truth on order_id."""
        ground_truth = {gt["order_id"]: gt for gt in self._load_json(self.ground_truth_path)}
        cases = [
            {**case, **ground_truth[case["order_id"]]}
            for case in self._load_json(self.input_data_path)
        ]
        self.log(f"Loaded {len(cases)} cases.")
        return cases

    # ---------------------------- agent ---------------------------- #
    async def _run_agent(self, case: dict) -> tuple[str, AgentResult]:
        session_id = str(uuid4())

        insert_starting_execution(
            execution_id=session_id,
            customer_id=case["customer_id"],
            order_id=case["order_id"],
            investigation_prompt=case["problem_description"],
        )
        upfront_data = get_upfront_data(
            customer_id=case["customer_id"],
            order_id=case["order_id"],
        )
        insert_upfront_data(
            execution_id=session_id,
            upfront_data=upfront_data.model_dump(mode="json"),
        )

        agent_result = await self.agent.run(
            upfront_data=upfront_data,
            investigation_prompt=case["problem_description"],
            session_id=session_id,
        )
        return session_id, agent_result

    # ---------------------------- judge ---------------------------- #
    @staticmethod
    def _user_input(agent_result: AgentResult, case: dict) -> str:
        return (
            f"AGENT RESULT\n\n"
            f"Investigation Report:\n{agent_result.investigation_report}\n\n"
            f"Evidences:\n{agent_result.evidences}\n\n"
            f"GROUND TRUTH\n\n"
            f"Actual Scenario:\n{case['actual_scenario']}\n\n"
            f"Supporting Evidence:\n{case['supporting_evidence']}\n"
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
    async def _evaluate_single_case(self, case: dict, run_id: str) -> dict:
        self.log(f"EVALUATING CASE: {case['input_id']} ({case['order_id']})")
        self.obs.init_eval_trace(run_id=run_id, case=case)

        record = {
            "run_id": run_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "input_id": case["input_id"],
            "order_id": case["order_id"],
            "scenario_subtype": case["scenario_subtype"],
        }

        try:
            session_id, agent_result = await self._run_agent(case)
            self.obs.log_execution_id(session_id)

            messages = self._make_messages(self._user_input(agent_result, case))
            # to_thread keeps the context, so the judge generation nests under this trace
            result = await asyncio.to_thread(self._call_llm, messages)
            self.obs.process_result(result)

            self.log(f"Score: {result.overall_score}, Passed: {result.overall_passed}")

            return {
                **record,
                "execution_id": session_id,
                "status": "ok",
                "error": None,
                "investigation_report": agent_result.investigation_report,
                "evidences": str(agent_result.evidences),
                **{criterion: getattr(result, criterion) for criterion in CRITERIA},
                "judge_reasoning": result.judge_reasoning,
                "overall_score": result.overall_score,
                "overall_passed": result.overall_passed,
            }

        except Exception as e:
            self.obs.process_failure(e)
            self.log(f"Error evaluating case {case['input_id']}: {e}")

            return {
                **record,
                "execution_id": None,
                "status": "error",
                "error": str(e),
                **{criterion: None for criterion in CRITERIA},
                "judge_reasoning": None,
                "overall_score": 0,
                "overall_passed": False,
            }

    # ---------------------------- saving ---------------------------- #
    def _save_execution(self, records: list[dict]):
        self.execution_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.execution_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=4, ensure_ascii=False, default=str)
        self.log(f"Execution results saved to {self.execution_path}")

    def _save_report(self, report: str):
        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.report_path, "w", encoding="utf-8") as f:
            f.write(report)
        self.log(f"Report saved to {self.report_path}")

    # ----------------------------- main ----------------------------- #
    async def evaluate(self, limit: int | None = None) -> list[dict]:
        """Evaluates every case. `limit` caps the number of cases (for smoke tests)."""
        run_id = str(uuid4())
        cases = self._load_cases()[:limit]
        records = []

        try:
            for i, case in enumerate(cases, start=1):
                records.append(await self._evaluate_single_case(case, run_id))

                if i < len(cases):
                    await asyncio.sleep(self.CASE_DELAY_SECONDS)  # usage limit buffer
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
    asyncio.run(AgentEvaluator().evaluate())