# Judge Calibration for the Delivery Investigator Agent

## Abstract

The Delivery Investigator Agent is scored by an LLM judge, so the judge must be tested before it is trusted. This report describes a calibration dataset of 15 mock agent outputs, each paired with its ground truth and an intended overall result. Ten outputs are good and five are bad. The judge scores three separate yes/no criteria on each case: cause correctness, evidence identification, and evidence consistency. If the judge returns the intended labels on all 15 cases, it is treated as calibrated enough for the wider evaluation set. The dataset is a small calibration tool, not a benchmark.

## 1. Introduction

An LLM judge is also a model, so it can make mistakes. If it is too lenient, it passes bad reports. If it is too strict, it fails good ones. Calibration means testing the judge on cases where we already know the right answer.

The judge returns three independent yes/no criteria:

- **cause\_correct:** Does the report identify the same cause as the ground truth (`actual_scenario`)? The agent's evidence list is not used for this.
- **evidence\_identification\_correct:** Did the agent cite the essential records listed in the ground truth (`supporting_evidence`)?
- **evidence\_consistency\_correct:** Are the report's important claims supported by the agent's own evidence list, without contradiction? The ground truth is not used for this.

The three criteria are independent. A report can name the right cause but cite weak evidence. It can also cite the right records but misread them. These labels are scored separately from `overall_passed`, which is the intended overall result of each case.

## 2. Dataset

### 2.1 Structure

Each record has three fields:

| Field | Description |
| --- | --- |
| `agent_result` | The agent's output: `investigation_report`, `evidences`, `investigation_success`, `confidence`. |
| `ground_truth` | The authoritative case record: `order_id`, `scenario_subtype`, `actual_scenario`, `supporting_evidence`. |
| `overall_passed` | The intended overall result, used as the reference label during calibration. |

### 2.2 Composition

The 15 cases cover the agent's known scenarios: documented delay, failed delivery attempt, delivered but not received, no recent tracking progress, apparent tracking conflict, address discrepancy (historical, unrecognized, historically valid), and pre-pickup stall (explained and unexplained).

**Cases 1 to 10 are good outputs.** All three criteria are expected to be true.

**Cases 11 to 15 are bad outputs.** At least one criterion is expected to be false. They are made subtle on purpose: each looks reasonable at first and fails for one specific reason.

### 2.3 The five bad cases

| Case | Scenario | Criteria expected false | Failure mode |
| --- | --- | --- | --- |
| 11 | Delivered, not received | cause\_correct | The report says the parcel was stolen. The records only show a doorstep delivery, so theft is a possibility, not a recorded fact. |
| 12 | Address discrepancy (historically valid) | cause\_correct | The report says the order went to an old address in error. The tool evidence shows the address was valid on the order date, so the mismatch alone is not an error. |
| 13 | Pre-pickup stall (quality hold) | evidence\_consistency\_correct | The report names `quality_hold` correctly, but the agent's evidence list does not include that event, only the inventory snapshot. |
| 14 | Apparent tracking conflict | evidence\_identification\_correct | The agent cites only the final delivered event and omits the earlier delivery exception that created the conflict. |
| 15 | Severe weather delay | cause\_correct, evidence\_consistency\_correct | The report blames a customs hold and gives a new ETA. The evidence shows a weather delay and no ETA. The right records were cited but misread. |

In each case the other criteria are expected to be true. For example, case 11 still has correct identification and consistency, because the cited records do support the report's own reasoning.

## 3. Design Rationale

Each criterion is failed alone or in a controlled pair:

- Cases 11 and 12 fail only cause\_correct.
- Case 13 fails only evidence\_consistency\_correct.
- Case 14 fails only evidence\_identification\_correct.
- Case 15 fails cause\_correct and evidence\_consistency\_correct, but not evidence\_identification\_correct.

This lets a reviewer check four things:

1. The judge gives the correct three-way label for each case, not just one pass or fail.
2. A correct cause does not hide an unsupported evidence trail (case 13).
3. Internal consistency does not hide a missing essential record (case 14).
4. "Cited the right records" is not confused with "reasoned correctly from them" (case 15).

## 4. Evaluation Procedure

1. Run the judge once on each of the 15 cases.
2. Compare its three labels with the intended labels for every case.
3. Count agreement for each criterion, and count false passes (judge says true, intended false) and false fails (judge says false, intended true).
4. Read the judge's reasoning for every disagreement to find which criterion it is misapplying.

If the judge returns the intended labels on all 15 cases, it is treated as calibrated enough for the wider evaluation set. If not, the judge prompt or rubric is revised and the calibration is run again. The intended labels are not changed to fit the judge.


## 5. Conclusion

This dataset is a basic trust check for the judge. It tests whether the judge can separate good from bad outputs and apply its three criteria independently. A judge that matches all intended labels can be used on the wider evaluation set. Later work should add more borderline cases, repeated runs, and real agent outputs checked by a human.
