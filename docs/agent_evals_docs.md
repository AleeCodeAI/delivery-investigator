# Delivery Investigator Agent — Evaluation Methodology

## 1. Overview

The purpose of the evaluation is to assess the quality and reliability of the Delivery Investigator Agent using an **LLM-as-a-Judge** approach.

The evaluation focuses exclusively on the Investigation Agent. Its primary responsibility is to identify the underlying cause of delivery problems and produce investigation reports supported by reliable evidence.

## 2. Definition of Success

A successful evaluation requires the Investigation Agent to achieve an overall pass rate of at least **90% across the 70 investigation cases**.

Success is determined using two evaluation criteria, each assigned a weight based on its importance:

| Criterion | Weight |
|---|---:|
| Cause correctness | 80% |
| Evidence consistency | 20% |
| **Total** | **100%** |

Each investigation receives a score based on these weights. An individual investigation passes when its score is at least **80 points**.

The overall evaluation is considered successful when at least **63 out of 70 investigations pass**, achieving the required 90% pass rate.

This means the agent must demonstrate that it can consistently identify the correct cause of delivery problems and produce reports supported by reliable evidence.

## 3. Evaluation Process

The evaluation consists of two separate stages: agent execution and agent evaluation.

### 3.1 Agent Execution

The agent execution stage uses `input_data.json`, which contains 70 investigation cases.

Each case provides the information required to initiate an investigation, including:

- Input ID
- Customer ID
- Order ID
- Problem description

An Agent Run File processes the cases individually, supplies the required information to the Investigation Agent, and collects its results.

The results are stored in an Agent Results File, which serves as the input for the evaluation stage.

### 3.2 Agent Evaluation

The evaluator does not execute the Investigation Agent. It evaluates the results already collected during the execution stage.

For each case, the evaluator receives:

- The corresponding agent result.
- The corresponding ground-truth record.

The LLM judge assesses the agent's `investigation_report` and `evidences` against the expected scenario and supporting information in the ground truth.

This separation allows agent execution and evaluation to be performed independently.

## 4. Ground-Truth Dataset

The evaluation uses 70 synthetic delivery investigation cases.

Each ground-truth record contains four fields:

| Field | Purpose |
|---|---|
| `order_id` | Identifies the order associated with the investigation. |
| `scenario_subtype` | Categorizes the specific delivery problem. |
| `actual_scenario` | Describes what actually happened and establishes the underlying cause. |
| `supporting_evidence` | Describes the relevant database records and information supporting the actual scenario. |

The `actual_scenario` and `supporting_evidence` fields are the primary reference information for the LLM judge.

Ground truth is intended to represent the expected investigation outcome accurately. Its quality is important because the judge relies on it when assessing the agent's conclusions.

## 5. Evaluation Criteria

The evaluation uses two binary criteria.

### 5.1 Cause Correctness (`cause_correct`)

Determines whether the agent correctly identifies the underlying cause of the delivery problem.

- **Ground truth:** `actual_scenario`
- **Agent output:** `investigation_report`

The judge compares the investigation report against the actual scenario.

The assessment focuses on whether the report correctly explains what happened and identifies the underlying cause. Different wording is acceptable as long as the explanation is semantically correct.

### 5.2 Evidence Consistency (`evidence_consistency_correct`)

Determines whether the claims and reasoning in the investigation report are adequately supported by the evidence identified by the agent.

- **Agent output:** `evidences` and `investigation_report`

The judge evaluates three aspects:

1. **Evidence support:** Important claims in the report must be supported by the identified evidence.
2. **Logical reasoning:** The explanation and causal reasoning must follow logically from the available evidence.
3. **No contradictions:** The report must not introduce important claims that contradict its identified evidence.

The report does not need to explicitly mention every evidence item. Its important claims and conclusions must, however, be grounded in the evidence.

## 6. Evaluation Philosophy and Scoring

The evaluation prioritizes the agent's actual purpose rather than treating every aspect of an investigation as equally important.

Identifying the correct cause is the primary responsibility of the Investigation Agent. Evidence consistency is also important because a correct conclusion should be supported by reliable information and logical reasoning.

### 6.1 Evaluation Weights

| Criterion | Weight |
|---|---:|
| Cause correctness | 80% |
| Evidence consistency | 20% |
| **Total** | **100%** |

Cause correctness receives the higher weight because reaching the correct conclusion is the agent's primary objective.

Evidence consistency evaluates the reliability of the explanation supporting that conclusion.

### 6.2 Scoring Method

Both criteria are binary:

- `True`: The criterion receives its full assigned weight.
- `False`: The criterion receives zero points.

**Overall score formula:**

`Overall Score = (cause_correct × 80) + (evidence_consistency_correct × 20)`

The score is calculated programmatically rather than by the LLM judge.

### 6.3 Individual Investigation Pass Threshold

An investigation passes when its overall score is at least 80%.

| Cause Correct | Evidence Consistency | Score | Result |
|---|---|---:|---|
| True | True | 100 | Pass |
| True | False | 80 | Pass |
| False | True | 20 | Fail |
| False | False | 0 | Fail |

This ensures that an investigation cannot pass if it identifies the wrong underlying cause, regardless of its evidence consistency.

## 7. Judge Calibration

The LLM judge must be calibrated to ensure that it applies the evaluation criteria consistently.

Calibration is performed separately from the 70-case evaluation dataset.

For the final methodology, **15 independently generated mock investigation cases** are used. These cases are not selected from the evaluation dataset.

### 7.1 Calibration Process

1. Generate 15 mock investigation cases.
2. Establish the expected evaluation judgments manually.
3. Run the LLM judge against the calibration cases.
4. Compare the judge's results with the manual judgments.
5. Review disagreements and adjust the judge instructions when necessary.

### 7.2 Calibration Results

The final calibration achieved **100% alignment** with the manual judgments.

This indicates that the judge correctly applied both evaluation criteria across the calibration cases.

Calibration should be repeated after significant changes to the judge's instructions or evaluation methodology.

## 8. Important Evaluation Considerations

### Ground-Truth Reliability

The ground truth is the reference against which the agent is evaluated. Incomplete or inaccurate ground-truth records can lead to incorrect judgments.

Therefore, ground-truth records must accurately represent the expected scenario and include the relevant supporting information.

### Semantic Evaluation

The judge should assess the meaning and correctness of the investigation rather than requiring exact wording.

An agent may explain the same underlying cause differently from the ground truth and should still receive credit when its reasoning is correct.

### Evidence Retrieved Through Tools

The Investigation Agent can retrieve additional information through tools during an investigation.

The judge should assess the actual evidence and information used by the agent, rather than penalizing it simply because the information was retrieved through a tool call.

The evaluation should distinguish between the method used to obtain information and whether that information supports the investigation.

### Independent Criterion Assessment

Each criterion should be assessed according to its own definition.

Cause correctness concerns whether the agent reached the correct conclusion. Evidence consistency concerns whether the report's claims and reasoning are supported by the evidence identified by the agent.

This keeps the evaluation focused on the two distinct responsibilities being assessed.

## 9. Conclusion

The evaluation methodology is designed to provide a focused assessment of the Delivery Investigator Agent's quality and reliability.

It separates agent execution from evaluation, uses ground-truth records as the reference for judging investigation outcomes, and applies two weighted criteria to assess correctness and evidence-based reasoning.

The LLM judge is calibrated against independently generated cases and manually established judgments to improve consistency.

Ultimately, the evaluation aims to answer two questions:

1. Did the agent correctly identify the underlying cause of the delivery problem?
2. Is its investigation report supported by the evidence it presents?

These questions reflect the core responsibilities of the Investigation Agent and provide the basis for assessing its reliability.