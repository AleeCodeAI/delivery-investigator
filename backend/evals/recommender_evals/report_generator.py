import math
from collections import Counter
from datetime import datetime, timezone

CRITERIA: tuple[str, ...] = (
    "recommendation_correct",
    "evidence_consistency_correct",
)


def generate_report(
    records: list[dict],
    run_id: str,
    judge_model: str,
    recommender_pass_rate: float = 90.0,
) -> str:
    """Builds a markdown summary of a recommender evaluation run from its execution records."""
    total = len(records)
    if total == 0:
        return "# Recommender Evaluation Report\n\nNo cases were evaluated.\n"

    # An errored case has no criterion verdicts (None) and counts as failed.
    judged = [r for r in records if r["recommendation_correct"] is not None]
    errors = total - len(judged)

    passed = sum(r["overall_passed"] for r in records)
    failed = total - passed
    pass_rate = passed / total * 100
    required = math.ceil(total * recommender_pass_rate / 100)
    scores = [r["overall_score"] for r in records]
    avg_score = sum(scores) / total

    lines = [
        "# Recommender Evaluation Report",
        "",
        f"- **Run ID:** `{run_id}`",
        f"- **Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC",
        f"- **Judge model:** {judge_model}",
        "",
        "## Overall Result",
        "",
        f"**{'PASS' if pass_rate >= recommender_pass_rate else 'FAIL'}**: {passed}/{total} recommendations passed "
        f"({pass_rate:.2f}%). Required: at least {required}/{total} ({recommender_pass_rate:.0f}%).",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Total cases | {total} |",
        f"| Passed (score >= {recommender_pass_rate}) | {passed} |",
        f"| Failed | {failed} |",
        f"| of which errored | {errors} |",
        f"| Pass rate | {pass_rate:.2f}% |",
        f"| Average overall score | {avg_score:.1f} |",
        f"| Lowest / highest score | {min(scores)} / {max(scores)} |",
        "",
        "## Score Distribution",
        "",
        "| Overall score | Cases |",
        "|---:|---:|",
    ]
    for score, count in sorted(Counter(scores).items(), reverse=True):
        lines.append(f"| {score} | {count} |")

    if judged:
        lines += [
            "",
            "## Criterion Pass Rates",
            "",
            "| Criterion | Passed | Rate |",
            "|---|---:|---:|",
        ]
        for key in CRITERIA:
            n = sum(bool(r[key]) for r in judged)
            lines.append(f"| {key} | {n}/{len(judged)} | {n / len(judged) * 100:.1f}% |")

    lines += [
        "",
        "## Individual Results",
        "",
        "| Case ID | Score | Result |",
        "|---|---:|---|",
    ]
    for r in records:
        if r["overall_passed"]:
            result = "PASS"
        elif r["recommendation_correct"] is None:
            result = "ERROR"
        else:
            result = "FAIL"
        lines.append(f"| {r['case_id']} | {r['overall_score']} | {result} |")

    failures = [r for r in records if not r["overall_passed"]]
    if failures:
        lines += ["", "## Failed Recommendations", ""]
        for r in failures:
            lines.append(f"### {r['case_id']}: score {r['overall_score']}")
            lines.append("")
            if r["recommendation_correct"] is not None:
                failed_criteria = [k for k in CRITERIA if not r[k]]
                lines.append(f"**Failed criteria:** {', '.join(failed_criteria) or 'none'}")
                lines.append("")
            lines.append(f"> {' '.join(r['judge_reasoning'].splitlines())}")
            lines.append("")

    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    import json
    from pathlib import Path
    from .recommender_evaluator import RecommenderEvaluator

    # For testing the report generator in isolation.
    records_path = Path(__file__).parent / "results" / "execution.json"
    with open(records_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    report = generate_report(
        records,
        run_id="test-run",
        judge_model="test-model",
        recommender_pass_rate=90.0,
    )
    RecommenderEvaluator()._save_report(report)