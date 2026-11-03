import json
import time
from pathlib import Path

from evals.agent_evals.agent_evaluator import AgentEvaluator
from utils.color import Logger


class AgentJudgeCalibration(Logger):
    """Runs the agent judge on hand-labeled mock outputs and saves its verdicts."""

    name: str = "AgentJudgeCalibration"
    color: str = Logger.CYAN

    def __init__(self):
        self.evaluator = AgentEvaluator()

        data_dir = self.evaluator.ground_truth_path.parent
        self.calibration_data = data_dir / "agent_judge_calibration_data.json"
        self.execution_result = Path(__file__).parent / "execution.json"

        self.log("AgentJudgeCalibration initialized successfully.")

    def _load_calibration_data(self) -> list[dict]:
        with open(self.calibration_data, encoding="utf-8") as file:
            data = json.load(file)
        self.log(f"Loaded {len(data)} calibration cases.")
        return data

    def _save_execution_results(self, results: list[dict]):
        with open(self.execution_result, "w", encoding="utf-8") as file:
            json.dump(results, file, indent=4, ensure_ascii=False)
        self.log(f"Execution results saved to {self.execution_result}")

    def _evaluate_single_case(self, item: dict) -> dict:
        case_id = item["case_id"]
        self.log(f"CALIBRATING CASE: {case_id}")

        try:
            agent_result = item["agent_result"]
            user_input = self.evaluator._user_input(agent_result, item["ground_truth"])
            messages = self.evaluator._make_messages(user_input)
            result = self.evaluator._call_llm(messages)

            self.log(f"Score: {result.overall_score}, Passed: {result.overall_passed}")
            return {
                "case_id": case_id,
                "cause_correct": result.cause_correct,
                "evidence_consistency_correct": result.evidence_consistency_correct,
                "overall_score": result.overall_score,
                "overall_passed": result.overall_passed,
                "judge_reasoning": result.judge_reasoning,
            }

        except Exception as e:
            self.log(f"Error calibrating case {case_id}: {e}")
            return {
                "case_id": case_id,
                "cause_correct": None,
                "evidence_consistency_correct": None,
                "overall_score": 0,
                "overall_passed": False,
                "judge_reasoning": f"ERROR: {e}",
            }

    def evaluate(self) -> list[dict]:
        """Runs the judge on every calibration case and saves the results."""
        data = self._load_calibration_data()
        execution_results = []

        try:
            for i, item in enumerate(data, start=1):
                execution_results.append(self._evaluate_single_case(item))

                if i < len(data):
                    time.sleep(self.evaluator.CASE_DELAY_SECONDS)  # API rate limit buffer
        finally:
            self._save_execution_results(execution_results)
            self.evaluator.obs.flush()

        return execution_results


if __name__ == "__main__":
    AgentJudgeCalibration().evaluate()