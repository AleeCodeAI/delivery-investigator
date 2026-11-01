# Judge Calibration Dataset — Delivery Investigator Agent

## 1. Purpose

This document describes a calibration dataset for an LLM-as-Judge evaluation of the Delivery Investigator Agent. The dataset contains 15 mock agent outputs paired with their ground truth. Its purpose is to test whether the judge reliably discriminates between correct and incorrect agent behaviour before the judge is trusted on real evaluation data.

The dataset is a **calibration instrument**, not a benchmark. It is small, hand-designed, and intended for manual inspection of judge behaviour.

## 2. Structure

Each record contains three fields:

| Field | Description |
|---|---|
| `agent_result` | The agent's output, following the `AgentResult` schema (investigation_report, evidences, investigation_success, confidence). |
| `ground_truth` | The authoritative case record (order_id, scenario_subtype, actual_scenario, supporting_evidence). |
| `overall_passed` | The intended overall outcome of the case, used as the reference label during calibration. |

The judge itself returns three independent binary criteria — `cause_correct`, `evidence_identification_correct`, and `evidence_consistency_correct` — which are scored separately from `overall_passed`.

## 3. Composition

The dataset contains 15 cases distributed across the agent's known scenario categories:

- documented shipment delay
- failed delivery attempt
- marked delivered, not received
- no recent tracking progress
- apparent tracking conflict
- address discrepancy (historical, unrecognized, historically valid)
- pre-pickup stall (explained and unexplained)

**Ten cases are good outputs** (all three criteria expected true). **Five cases are bad outputs** (at least one criterion expected false). The bad cases were designed to be subtle: each is plausible on a first read and fails for a specific, identifiable reason rather than an obvious error.

## 4. Failure Modes in the Bad Cases

The five bad cases fail different criteria so that the judge's three-way labelling can be verified independently. The table below lists each bad case, its scenario, the criteria it should fail, and the specific reason.

| Case | Scenario | Failing criteria | Failure mode |
|---|---|---|---|
| 11 | Marked delivered, not received | `cause_correct` | The report concludes the parcel was **stolen** after a doorstep delivery. The ground truth states only that the carrier recorded a doorstep delivery and that receipt is not established. Theft is a possibility, not a recorded fact, so the report asserts a cause the records do not support. Evidence identification and consistency remain correct because the cited records do support the report's own reasoning. |
| 12 | Address discrepancy (historically valid) | `cause_correct` | The report concludes the order was sent to an **old address in error**. The tool evidence shows the destination was effective on the order date (effective_to after order_date), so the address was historically valid and the mismatch alone does not establish an error. The report's own evidence is consistent with its claim, so only cause correctness fails. |
| 13 | Pre-pickup stall with quality hold | `evidence_consistency_correct` | The report correctly names a `quality_hold` event as the cause, but the agent's `evidences` list **does not include** the quality_hold inventory_event — only the inventory context snapshot. The causal claim is therefore not supported by the agent's own cited evidence. Cause correctness and evidence identification remain correct because the named cause matches ground truth and the essential record was in fact retrievable. |
| 14 | Apparent tracking conflict | `evidence_identification_correct` | The agent cites only the final delivered event and omits the **earlier delivery_exception** that created the apparent conflict. The ground-truth essential evidence includes both events, since the conflict and its resolution are the point of the case. The report is internally consistent with the evidence it did cite, so consistency remains correct. |
| 15 | Severe weather delay | `cause_correct`, `evidence_consistency_correct` | The report states the delay was caused by a **customs hold** and provides a **new delivery ETA**. The cited evidence records a severe weather delay and contains no ETA. The cause is wrong relative to ground truth, and the report contradicts its own evidence. Evidence identification is correct: the agent cited the right records, it simply misread and embellished them. |

## 5. Design Rationale

The bad cases were constructed so that each criterion is failed in isolation or in a controlled combination:

- Case 11 and case 12 fail **only** `cause_correct`.
- Case 13 fails **only** `evidence_consistency_correct`.
- Case 14 fails **only** `evidence_identification_correct`.
- Case 15 fails **both** `cause_correct` and `evidence_consistency_correct`, but not `evidence_identification_correct`.

This distribution lets a reviewer check that the judge:

1. produces the correct three-way label per case, not just a single pass/fail;
2. does not let a correct cause mask an unsupported evidence trail (case 13);
3. does not let internal consistency mask a missing essential record (case 14);
4. does not confuse "cited the right records" with "reasoned correctly from them" (case 15).

If the judge returns the intended labels on all 15 cases, it is treated as calibrated enough to be used on the wider evaluation set. If it does not, the discrepancy indicates which criterion the judge is misapplying, and the judge prompt or rubric is revised accordingly.

## 6. Limitations

The dataset is small and synthetic. It covers the scenario categories defined in the project specification but does not cover every subtype in depth. It is intended to detect gross judge misbehaviour, not to measure judge accuracy precisely. Cases are hand-written and may reflect the author's assumptions about what a plausible agent error looks like; real agent outputs may fail in ways not represented here.