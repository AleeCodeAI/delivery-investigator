import math
from collections import Counter
from datetime import datetime, timezone

from schemas import AgentEvalsResult

CRITERIA: tuple[str, ...] = (
    "cause_correct",
    "evidence_identification_correct",
    "evidence_consistency_correct",
)


def generate_report(
    records: list[dict],
    run_id: str,
    judge_model: str,
    agent_pass_rate: float = 90.0,
) -> str:
    """Builds a markdown summary of an evaluation run from its execution records."""
    total = len(records)
    if total == 0:
        return "# Agent Evaluation Report\n\nNo cases were evaluated.\n"

    passed = sum(r["overall_passed"] for r in records)
    failed = total - passed
    errors = sum(r["status"] == "error" for r in records)
    pass_rate = passed / total * 100
    required = math.ceil(total * agent_pass_rate / 100)
    agent_passed = pass_rate >= agent_pass_rate
    scores = [r["overall_score"] for r in records]
    avg_score = sum(scores) / total

    lines = [
        "# Agent Evaluation Report",
        "",
        f"- **Run ID:** `{run_id}`",
        f"- **Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC",
        f"- **Judge model:** {judge_model}",
        "",
        "## Overall Result",
        "",
        f"**{'PASS' if agent_passed else 'FAIL'}**: {passed}/{total} investigations passed "
        f"({pass_rate:.2f}%). Required: at least {required}/{total} ({agent_pass_rate:.0f}%).",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Total cases | {total} |",
        f"| Passed (score >= {AgentEvalsResult.PASS_THRESHOLD}) | {passed} |",
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

    judged = [r for r in records if r["status"] == "ok"]
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
        "| Input ID | Order ID | Scenario | Score | Result |",
        "|---|---|---|---:|---|",
    ]
    for r in records:
        result = "PASS" if r["overall_passed"] else ("ERROR" if r["status"] == "error" else "FAIL")
        lines.append(
            f"| {r['input_id']} | {r['order_id']} | {r['scenario_subtype']} | {r['overall_score']} | {result} |"
        )

    failures = [r for r in records if not r["overall_passed"]]
    if failures:
        lines += ["", "## Failed Investigations", ""]
        for r in failures:
            lines.append(f"### {r['input_id']} ({r['order_id']}): score {r['overall_score']}")
            lines.append("")
            if r["status"] == "error":
                lines.append(f"**Error:** {r['error']}")
            else:
                failed_criteria = [k for k in CRITERIA if not r[k]]
                lines.append(f"**Failed criteria:** {', '.join(failed_criteria) or 'none'}")
                lines.append("")
                lines.append(f"> {' '.join(r['judge_reasoning'].splitlines())}")
            lines.append("")

    return "\n".join(lines) + "\n"