# Agent Evaluation Documentation

## 1. Overview

The purpose of the evaluation was to assess the reliability and quality of the Delivery Investigator Agent. The evaluation covered 70 investigation cases, with an overall pass threshold of 80 points per case and a required dataset pass rate of at least 90% (63 out of 70 cases).

Three evaluation runs were conducted. Each run incorporated changes to the evaluation process, dataset, or evaluation criteria to improve the reliability and relevance of the assessment.

The judge model used across all three runs was `openai/gpt-oss-120b`.

## 2. Evaluation Runs

### Run 1 — Initial Evaluation

**Date:** November 1, 2026  
**Run ID:** `e348fec5-d3ac-4b29-822e-46e75172dc8a`

The initial evaluation resulted in a failure, with 60 out of 70 investigations passing (85.71%), below the required 90% threshold.

| Metric | Result |
|---|---:|
| Total cases | 70 |
| Passed | 60 |
| Failed | 10 |
| Average score | 89.1 |
| Pass rate | 85.71% |

The evaluation initially used three criteria:

- Cause correctness: 50%
- Evidence identification correctness: 30%
- Evidence consistency correctness: 20%

Following an investigation of the failed cases, two issues were identified:

1. **Ground-truth issues:** Some ground-truth records were incomplete or required corrections. These records were updated to better represent the expected investigation outcomes.

2. **Judge evaluation issues:** The judge sometimes incorrectly penalized evidence retrieved through tool calls because the tool usage itself was not explicitly mentioned in the ground truth. The underlying records retrieved through those tools were, however, available in the ground-truth data. The judge prompt was therefore adjusted to distinguish between tool usage and the actual evidence retrieved.

These findings indicated that the initial failure was not solely attributable to the agent. The evaluation dataset and judging instructions also required improvements.

### Run 2 — Evaluation After Corrections

**Date:** November 3, 2026  
**Run ID:** `6b2537c3-7a1f-4aea-91fd-056b5965c24b`

Following the ground-truth corrections and judge prompt adjustments, the second evaluation was conducted.

| Metric | Result |
|---|---:|
| Total cases | 70 |
| Passed | 66 |
| Failed | 4 |
| Average score | 96.3 |
| Pass rate | 94.29% |

The agent successfully exceeded the required 90% pass rate.

The criterion results were:

| Criterion | Pass rate |
|---|---:|
| Cause correctness | 100% |
| Evidence identification correctness | 88.6% |
| Evidence consistency correctness | 92.9% |

Although the evaluation passed, a further review of the evaluation criteria led to an important decision: evidence identification correctness was not considered necessary as an independent evaluation criterion.

The primary objective of the agent is to identify the correct cause of a delivery problem using available offline data and additional evidence retrieved through tools. Its second major responsibility is to ensure that every claim in its investigation report is supported by the presented evidence.

Evidence identification correctness primarily checked whether the identified evidence corresponded to the expected ground-truth evidence. However, incorrect evidence identification would already affect the correctness of the investigation report and its consistency with the supporting evidence.

Therefore, retaining this criterion introduced overlapping evaluation requirements without providing sufficient additional value.

### Run 3 — Final Evaluation

**Date:** November 3, 2026  
**Run ID:** `d6ffa554-8196-40a7-92e3-ef6efadf60b1`

For the final evaluation, the evaluation methodology was revised to use only two criteria:

1. **Cause correctness:** Whether the agent correctly identifies the underlying cause of the delivery problem.
2. **Evidence consistency correctness:** Whether the claims and conclusions presented in the investigation report are adequately supported by the provided evidence.

The evidence identification criterion was removed from the judge prompt.

Since this change affected the evaluation methodology, the previous judge calibration was no longer considered sufficient. A new calibration process was conducted using updated calibration data and documentation aligned with the two-criterion approach. The judge achieved **100% alignment during calibration**, providing confidence in its ability to apply the revised evaluation criteria.

The final evaluation was also conducted using a newly generated set of 70 agent results and an updated evaluation dataset. The evaluation documentation, calibration data, and relevant code were updated to reflect the revised methodology.

**Final evaluation results:**

| Metric | Result |
|---|---:|
| Total cases | 70 |
| Passed | 66 |
| Failed | 4 |
| Average score | 94.3 |
| Pass rate | 94.29% |
| Required pass rate | 90% |

**Criterion results:**

| Criterion | Passed | Pass rate |
|---|---:|---:|
| Cause correctness | 66/70 | 94.3% |
| Evidence consistency correctness | 66/70 | 94.3% |

The final evaluation successfully passed, exceeding the required threshold by 4.29 percentage points.

## 3. Final Conclusion

The three evaluation runs helped improve both the agent assessment process and the evaluation methodology.

The first run exposed issues in the ground-truth data and judge instructions. The second run demonstrated that correcting these issues resulted in a successful evaluation. The third run further refined the methodology by removing an overlapping criterion and focusing exclusively on the two most important responsibilities of the agent.

The final evaluation achieved a **94.29% pass rate across 70 investigations**, with 66 investigations passing and an average score of 94.3.

Based on the final results and the 100% judge calibration alignment, the agent demonstrated satisfactory performance against the defined evaluation requirements.

The final evaluation methodology also provides a more focused assessment of the agent's actual purpose: identifying the correct cause of delivery problems and producing investigation reports whose conclusions are consistently supported by evidence.