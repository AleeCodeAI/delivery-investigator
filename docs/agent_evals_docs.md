# Agent Evaluator Documentation

## 1. Overview

The Agent Evaluator assesses the quality and reliability of the Delivery Investigator Agent using an LLM-as-a-Judge approach against a predefined ground-truth dataset.

The evaluation focuses on three main areas:

- Correctly identifying the cause of the delivery issue.
- Identifying the essential supporting evidence.
- Producing a report whose claims and reasoning are consistently supported by the identified evidence.

Each investigation receives individual evaluation results and a weighted overall score.

**Scope:** This evaluation focuses exclusively on the Investigation Agent. It does not evaluate the Recommender, the main application pipeline, or the overall Delivery Investigator system.

## 2. Evaluation Criteria

The evaluator assesses the agent using three binary criteria.

### 2.1 Cause Correctness (`cause_correct`)

Determines whether the agent correctly identifies the cause of the delivery issue.

- **Ground truth:** `actual_scenario`
- **Agent output:** `investigation_report`

The judge compares the agent's investigation report against the actual scenario recorded in the ground truth.

The evaluation focuses on whether the report correctly explains what happened and identifies the underlying cause of the delivery issue.

Different wording is acceptable as long as the explanation is semantically correct.

### 2.2 Evidence Identification Correctness (`evidence_identification_correct`)

Determines whether the agent identifies the essential supporting evidence expected for the investigation.

- **Ground truth:** `supporting_evidence`
- **Agent output:** `evidences`

The judge compares the evidence identified by the agent against the ground-truth supporting evidence.

The evaluation focuses on whether the agent identifies the important records that establish the actual scenario.

The following principles apply:

1. **Essential evidence:** The agent is not required to identify every evidence item in the ground truth. It must identify the essential records needed to establish the actual scenario. Missing supplementary or incidental records should not automatically result in failure.
2. **Semantic matching:** Evidence descriptions do not need to match the ground truth word for word. Different wording is acceptable when they refer to the same underlying record and information.
3. **Relevance:** Merely identifying records related to the order or delivery issue is insufficient. The identified evidence must correspond to the important facts established by the ground truth.

### 2.3 Evidence Consistency Correctness (`evidence_consistency_correct`)

Determines whether the agent appropriately uses the evidence it identified to support the claims and reasoning in its investigation report.

- **Agent output:** `evidences`, `investigation_report`

The judge evaluates whether the important factual claims and reasoning in the investigation report are supported by the evidence identified by the agent.

The following principles apply:

1. **Evidence support:** Important claims in the report should be supported by the identified evidence.
2. **Logical reasoning:** The explanation and causal reasoning should follow logically from the identified evidence.
3. **No contradictions:** The report should not introduce important claims that contradict the identified evidence.

The report does not need to explicitly quote or mention every evidence item. Its important claims and reasoning must, however, be grounded in the identified evidence.

**Important distinction:** Evidence consistency does not evaluate whether the final conclusion matches the actual scenario. That responsibility belongs to `cause_correct`, which compares the investigation report against `actual_scenario`.

This separation allows the evaluator to distinguish between identifying the correct evidence, reasoning appropriately from that evidence, and reaching the correct final conclusion.

## 3. Ground-Truth Dataset

The evaluation uses an existing dataset of 70 synthetic delivery investigation cases.

Each case contains the following ground-truth fields relevant to this evaluation:

| Field | Description |
|---|---|
| `actual_scenario` | Describes what actually happened in the delivery investigation. |
| `supporting_evidence` | Identifies the evidence expected to support the investigation. |

### Dataset Considerations

- The existing 70 cases are used rather than generating another dataset.
- Cases are designed to represent different delivery investigation scenarios.
- Agent development relies on general instructions and reasoning principles rather than case-specific prompt optimization.
- The dataset provides a practical benchmark for evaluating the agent against known scenarios.
- Since the dataset is synthetic, its results alone do not establish real-world generalization.

Future evaluations can expand the dataset with verified historical operational cases and additional custom test scenarios.

## 4. LLM-as-a-Judge

An LLM judge evaluates each investigation by comparing the relevant ground-truth information against the agent's outputs.

The judge returns:

- `cause_correct`
- `evidence_identification_correct`
- `evidence_consistency_correct`
- `judge_reasoning`

### Evaluation Principles

1. **Semantic evaluation:** Judge the meaning and correctness of the outputs rather than requiring exact wording.
2. **Evidence-based evaluation:** Base judgments on the provided ground truth and agent outputs.
3. **Independent evaluation:** Evaluate each criterion according to its defined responsibility without duplicating other criteria.
4. **No unsupported assumptions:** Do not assume information that is not present in the provided data.
5. **Consistency:** Apply the same evaluation standards across all cases.

The judge instructions should focus on general evaluation principles rather than case-specific rules.

## 5. Judge Calibration

Before evaluating the remaining cases, the judge is calibrated using 15 selected cases from the existing dataset.

### Calibration Process

1. Select 15 cases from the 70 available cases.
2. Manually establish the correct evaluation results for all three criteria.
3. Run the LLM judge on the same cases.
4. Compare the judge's results against the manual judgments.
5. Review disagreements and improve the judge's instructions or evaluation criteria when necessary.

### Agreement Rate

The agreement rate measures how often the judge's evaluations match the manual judgments.

**Formula:**

Agreement Rate = (Matching Judgments / Total Judgments) × 100

The initial calibration target is at least 90% agreement across the evaluation criteria.

Calibration validates the judge's ability to apply the evaluation standards consistently. It should not be used to make the judge agree with particular agent outputs regardless of correctness.

Calibration should be repeated after significant changes to the judge's instructions or evaluation methodology.

## 6. Evaluation Output and Scoring

Each investigation receives a weighted score based on its three evaluation criteria.

### Evaluation Weights

| Criterion | Weight |
|---|---:|
| Cause correctness | 60% |
| Evidence identification correctness | 20% |
| Evidence consistency correctness | 20% |
| **Total** | **100%** |

Cause correctness receives the highest weight because identifying the actual cause of the delivery issue is the primary responsibility of the Investigation Agent. The two evidence criteria assess whether the investigation identifies the essential supporting records and reasons reliably from them.

### Scoring Method

Each criterion is binary:

- `True`: The criterion receives its full assigned weight.
- `False`: The criterion receives zero points.

**Formula:**

Overall Score = (Cause Correct × 60) + (Evidence Identification Correct × 20) + (Evidence Consistency Correct × 20)

The score is calculated in Python rather than by the LLM judge.

### Individual Investigation Pass Threshold

An investigation passes when its overall score is at least 80%.

With the 60/20/20 weighting, an investigation with an incorrect cause can score at most 40%, even if both evidence criteria pass. This reflects the primary importance of reaching the correct conclusion.

The evaluation output includes:

- Individual criterion results.
- `judge_reasoning`
- `overall_score`
- `overall_passed`

## 7. Overall Agent Evaluation

After reserving 15 cases for judge calibration, the remaining 55 cases are used for agent evaluation.

### Overall Pass Criteria

The agent passes the overall evaluation when at least 90% of the 55 evaluation cases pass individually.

**Formula:**

Overall Pass Rate = (Passed Investigations / Total Evaluation Cases) × 100

At least 50 out of 55 investigations must pass.

| Passed Investigations | Pass Rate | Overall Result |
|---:|---:|---|
| 49/55 | 89.09% | Fail |
| 50/55 | 90.91% | Pass |
| 51/55 | 92.73% | Pass |
| 55/55 | 100% | Pass |

This provides one clear aggregate acceptance threshold while preserving individual results for identifying weaknesses in the agent.

## 8. Evaluation Integrity and Future Improvements

To maintain the reliability of the evaluation:

- Ground-truth labels must represent the actual intended scenario and must not be modified to accommodate agent results.
- Evaluation criteria and weights should remain fixed during a formal evaluation.
- Agent improvements should focus on general reasoning principles and responsibilities rather than case-specific prompt instructions.
- Judge calibration should be repeated after significant changes to its instructions or methodology.
- Evaluation results should be retained to compare different versions of the agent.

### Future Improvements

Potential improvements include:

- Expanding the dataset with verified real-world investigation cases.
- Adding more edge cases and previously unseen scenarios.
- Reviewing disagreements between manual judgments and the LLM judge.
- Improving evaluation criteria and methodology as new limitations are identified.

## 9. Final Evaluation Standards

| Component | Standard |
|---|---|
| Evaluation scope | Investigation Agent only |
| Evaluation method | LLM-as-a-Judge |
| Ground-truth dataset | 70 synthetic cases |
| Judge calibration | 15 cases |
| Agent evaluation | 55 cases |
| Evaluation criteria | Cause correctness, evidence identification, evidence consistency |
| Cause weight | 60% |
| Evidence identification weight | 20% |
| Evidence consistency weight | 20% |
| Individual investigation pass threshold | 80% |
| Judge calibration target | 90% agreement |
| Overall agent pass threshold | 90% |
| Minimum passed investigations | 50 out of 55 |

### Final Objective

Establish a consistent and measurable evaluation process that determines whether the Investigation Agent can correctly identify delivery issues, identify essential supporting evidence, and produce a reliable investigation report whose conclusions and reasoning are grounded in that evidence.
