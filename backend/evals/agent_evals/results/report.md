# Agent Evaluation Report

- **Run ID:** `6b2537c3-7a1f-4aea-91fd-056b5965c24b`
- **Generated:** 2026-11-03 11:33:30 UTC
- **Judge model:** openai/gpt-oss-120b

## Overall Result

**PASS**: 66/70 investigations passed (94.29%). Required: at least 63/70 (90%).

| Metric | Value |
|---|---:|
| Total cases | 70 |
| Passed (score >= 80) | 66 |
| Failed | 4 |
| of which errored | 0 |
| Pass rate | 94.29% |
| Average overall score | 96.3 |
| Lowest / highest score | 60 / 100 |

## Score Distribution

| Overall score | Cases |
|---:|---:|
| 100 | 61 |
| 80 | 5 |
| 60 | 4 |

## Criterion Pass Rates

| Criterion | Passed | Rate |
|---|---:|---:|
| cause_correct | 70/70 | 100.0% |
| evidence_identification_correct | 62/70 | 88.6% |
| evidence_consistency_correct | 65/70 | 92.9% |

## Individual Results

| Case ID | Score | Result |
|---|---:|---|
| ORD-189001 | 100 | PASS |
| ORD-189002 | 100 | PASS |
| ORD-189003 | 100 | PASS |
| ORD-189004 | 100 | PASS |
| ORD-189005 | 100 | PASS |
| ORD-189006 | 100 | PASS |
| ORD-189007 | 100 | PASS |
| ORD-189008 | 100 | PASS |
| ORD-189009 | 100 | PASS |
| ORD-189010 | 60 | FAIL |
| ORD-189011 | 80 | PASS |
| ORD-189012 | 80 | PASS |
| ORD-189013 | 100 | PASS |
| ORD-189014 | 100 | PASS |
| ORD-189015 | 100 | PASS |
| ORD-189016 | 60 | FAIL |
| ORD-189017 | 100 | PASS |
| ORD-189018 | 100 | PASS |
| ORD-189019 | 60 | FAIL |
| ORD-189020 | 80 | PASS |
| ORD-189021 | 100 | PASS |
| ORD-189022 | 100 | PASS |
| ORD-189023 | 100 | PASS |
| ORD-189024 | 80 | PASS |
| ORD-189025 | 100 | PASS |
| ORD-189026 | 100 | PASS |
| ORD-189027 | 100 | PASS |
| ORD-189028 | 100 | PASS |
| ORD-189029 | 100 | PASS |
| ORD-189030 | 100 | PASS |
| ORD-189031 | 100 | PASS |
| ORD-189032 | 100 | PASS |
| ORD-189033 | 100 | PASS |
| ORD-189034 | 100 | PASS |
| ORD-189035 | 100 | PASS |
| ORD-189036 | 100 | PASS |
| ORD-189037 | 100 | PASS |
| ORD-189038 | 100 | PASS |
| ORD-189039 | 100 | PASS |
| ORD-189040 | 100 | PASS |
| ORD-189041 | 100 | PASS |
| ORD-189042 | 100 | PASS |
| ORD-189043 | 100 | PASS |
| ORD-189044 | 100 | PASS |
| ORD-189045 | 100 | PASS |
| ORD-189046 | 100 | PASS |
| ORD-189047 | 100 | PASS |
| ORD-189048 | 100 | PASS |
| ORD-189049 | 100 | PASS |
| ORD-189050 | 100 | PASS |
| ORD-189051 | 100 | PASS |
| ORD-189052 | 100 | PASS |
| ORD-189053 | 100 | PASS |
| ORD-189054 | 100 | PASS |
| ORD-189055 | 100 | PASS |
| ORD-189056 | 100 | PASS |
| ORD-189057 | 60 | FAIL |
| ORD-189058 | 100 | PASS |
| ORD-189059 | 80 | PASS |
| ORD-189060 | 100 | PASS |
| ORD-189061 | 100 | PASS |
| ORD-189062 | 100 | PASS |
| ORD-189063 | 100 | PASS |
| ORD-189064 | 100 | PASS |
| ORD-189065 | 100 | PASS |
| ORD-189066 | 100 | PASS |
| ORD-189067 | 100 | PASS |
| ORD-189068 | 100 | PASS |
| ORD-189069 | 100 | PASS |
| ORD-189070 | 100 | PASS |

## Failed Investigations

### ORD-189010: score 60

**Failed criteria:** evidence_identification_correct, evidence_consistency_correct

> Cause: The report correctly states that the carrier attempted delivery and failed because it could not access the location, matching the actual scenario. Evidence identification: The agent listed all required shipment events but omitted the shipment record (SHIP-189010) that shows the delivery_attempted status, which is part of the ground‑truth supporting evidence, so an essential piece is missing. Evidence consistency: The report’s factual claims about the timeline and failed attempt are backed by the listed events, but the claim that the current shipment status is delivery_attempted is not supported by any provided evidence, making the report inconsistent with its own evidences.

### ORD-189016: score 60

**Failed criteria:** evidence_identification_correct, evidence_consistency_correct

> Cause: The report matches the ground‑truth scenario, correctly describing the two failed delivery attempts and the unchanged delivery_attempted status. Evidence identification: The agent listed the two failed shipment events and a status record, but omitted the explicit null delivered_at and missing delivery confirmation details that are part of the essential supporting evidence. Evidence consistency: The report’s claims about the reasons for each failed attempt are backed by the two event evidences, but the statements that there were no further carrier updates and no delivery confirmation are not directly supported by the provided evidences, making the report insufficiently grounded.

### ORD-189019: score 60

**Failed criteria:** evidence_identification_correct, evidence_consistency_correct

> Cause: The report correctly states that the carrier left the package at the front door of the correct address and that receipt cannot be confirmed, matching the ground‑truth scenario. Evidence identification: The agent only listed shipment event records, omitting the order record (status delivered and address match) and the shipment record (delivery confirmation left_at_door) that are essential in the ground truth, so essential evidence is missing. Evidence consistency: The claim that the package was left at the correct address is not supported by the provided evidences, which contain no address information; thus an important claim lacks backing, making the report inconsistent with its own evidence.

### ORD-189057: score 60

**Failed criteria:** evidence_identification_correct, evidence_consistency_correct

> Cause: The report correctly identifies the allocation failure and backorder flag as the reason the order was never picked up, matching the ground‑truth scenario. Evidence identification: The agent provided the two inventory events and the shipment label creation, but omitted the explicit order‑status=processing record and the evidence of no carrier‑pickup event, which are essential items in the ground‑truth supporting evidence. Evidence consistency: While the report’s claims about the inventory failures are backed by the provided inventory events, the statements that the parcel was never picked up and that the order remained in processing are not directly supported by any listed evidence (no pickup‑absence record or order‑status record), so the report is not fully consistent with its own evidence.

