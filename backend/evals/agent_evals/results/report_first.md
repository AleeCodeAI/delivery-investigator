# Agent Evaluation Report

- **Run ID:** `e348fec5-d3ac-4b29-822e-46e75172dc8a`
- **Generated:** 2026-11-01 10:24:09 UTC
- **Judge model:** openai/gpt-oss-120b

## Overall Result

**FAIL**: 60/70 investigations passed (85.71%). Required: at least 63/70 (90%).

| Metric | Value |
|---|---:|
| Total cases | 70 |
| Passed (score >= 80) | 60 |
| Failed | 10 |
| of which errored | 0 |
| Pass rate | 85.71% |
| Average overall score | 89.1 |
| Lowest / highest score | 20 / 100 |

## Score Distribution

| Overall score | Cases |
|---:|---:|
| 100 | 51 |
| 80 | 9 |
| 60 | 3 |
| 40 | 5 |
| 20 | 2 |

## Criterion Pass Rates

| Criterion | Passed | Rate |
|---|---:|---:|
| cause_correct | 63/70 | 90.0% |
| evidence_identification_correct | 59/70 | 84.3% |
| evidence_consistency_correct | 64/70 | 91.4% |

## Individual Results

| Case ID | Score | Result |
|---|---:|---|
| ORD-189001 | 100 | PASS |
| ORD-189002 | 100 | PASS |
| ORD-189003 | 100 | PASS |
| ORD-189004 | 100 | PASS |
| ORD-189005 | 100 | PASS |
| ORD-189006 | 80 | PASS |
| ORD-189007 | 100 | PASS |
| ORD-189008 | 100 | PASS |
| ORD-189009 | 100 | PASS |
| ORD-189010 | 100 | PASS |
| ORD-189011 | 100 | PASS |
| ORD-189012 | 80 | PASS |
| ORD-189013 | 100 | PASS |
| ORD-189014 | 100 | PASS |
| ORD-189015 | 100 | PASS |
| ORD-189016 | 40 | FAIL |
| ORD-189017 | 100 | PASS |
| ORD-189018 | 100 | PASS |
| ORD-189019 | 20 | FAIL |
| ORD-189020 | 80 | PASS |
| ORD-189021 | 40 | FAIL |
| ORD-189022 | 100 | PASS |
| ORD-189023 | 100 | PASS |
| ORD-189024 | 80 | PASS |
| ORD-189025 | 100 | PASS |
| ORD-189026 | 100 | PASS |
| ORD-189027 | 80 | PASS |
| ORD-189028 | 100 | PASS |
| ORD-189029 | 100 | PASS |
| ORD-189030 | 100 | PASS |
| ORD-189031 | 80 | PASS |
| ORD-189032 | 80 | PASS |
| ORD-189033 | 100 | PASS |
| ORD-189034 | 40 | FAIL |
| ORD-189035 | 40 | FAIL |
| ORD-189036 | 20 | FAIL |
| ORD-189037 | 40 | FAIL |
| ORD-189038 | 100 | PASS |
| ORD-189039 | 100 | PASS |
| ORD-189040 | 100 | PASS |
| ORD-189041 | 100 | PASS |
| ORD-189042 | 100 | PASS |
| ORD-189043 | 100 | PASS |
| ORD-189044 | 60 | FAIL |
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
| ORD-189068 | 60 | FAIL |
| ORD-189069 | 80 | PASS |
| ORD-189070 | 100 | PASS |

## Failed Investigations

### ORD-189016: score 40

**Failed criteria:** cause_correct

> Cause: the report adds a second failure reason (carrier could not access location) that is not present in the ground‑truth scenario, which only cites a business‑closed failure, so the cause is incorrect. Evidence identification: the agent supplied the key failed‑attempt record SE‑189100 and the shipment status, which are sufficient to establish the actual scenario; missing SE‑189101 and preceding events does not affect essential evidence, so identification is correct. Evidence consistency: all factual statements in the report (business‑closed attempt, access‑issue attempt, and current delivery_attempted status) are directly backed by the three evidences the agent listed, so the report is consistent with its evidence.

### ORD-189019: score 20

**Failed criteria:** cause_correct, evidence_identification_correct

> Cause: Report notes delivery left at the door but does not assert that the customer did not receive the item, so it fails to identify the genuine non‑receipt cause. Evidence identification: Agent listed all shipment events but omitted the shipment summary (SHIP-189019) and the order record (ORD-189019), which are essential for confirming delivery status and correct address. Evidence consistency: The report’s claims (delivery left at front door, no evidence of retrieval or theft) are directly supported by the provided shipment events, so the report is consistent with its evidences.

### ORD-189021: score 40

**Failed criteria:** cause_correct

> Cause: The report lists the delivery record and lack of further evidence but does not state that the customer genuinely did not receive the item, which is the ground‑truth cause, so cause_correct is false. Evidence identification: The agent supplied the delivered event (SE‑189137) and the matching address, the essential records needed to establish the scenario, so evidence_identification_correct is true. Evidence consistency: The report’s claims about delivery time, handed_to_resident, address match, and absence of additional records are all directly supported by the identified evidences, so evidence_consistency_correct is true.

### ORD-189034: score 40

**Failed criteria:** cause_correct

> Cause: The report attributes the issue to recipient unavailability, whereas the ground truth describes an apparent same‑day dispatch conflict resolved by ordering timestamps, so the cause is incorrect. Evidence identification: The agent listed all required shipment event records (SE‑189195‑203); the missing shipment status record is supplementary, not essential for establishing delivery, so identification is acceptable. Evidence consistency: All factual claims in the report (pickup, failed first attempt, successful second attempt at 16:30 left‑at‑door) are directly supported by the listed events, and no contradictions appear.

### ORD-189035: score 40

**Failed criteria:** cause_correct

> Cause: The report cites an access‑issue cause, but the ground truth attributes the problem to an apparent conflict resolved by ordering timestamps, so the cause is incorrect. Evidence identification: The agent provided the core shipment events (SE‑189209‑212) that establish the out‑for‑delivery, failed attempt, retry and delivery, matching the essential evidence; missing other events does not affect correctness. Evidence consistency: The timeline and delivery details described in the report are directly supported by the listed events, so the report is consistent with its evidence.

### ORD-189036: score 20

**Failed criteria:** cause_correct, evidence_identification_correct

> Cause: The report says there is no contradictory timestamps, but the ground truth states there was an apparent conflict due to a late‑synced facility scan, so the cause is misidentified. Evidence identification: The agent listed all shipment events but omitted the shipment record (SHIP-189036) that confirms delivery status, which is essential to the scenario. Evidence consistency: The claim of a consistent chronological sequence is directly supported by the listed events, so the report is consistent with its own evidence.

### ORD-189037: score 40

**Failed criteria:** cause_correct

> Cause: the report says there is no conflict, but the ground truth describes an apparent conflict caused by a late‑synced failed attempt, so the cause is misidentified. Evidence identification: the agent listed the three key shipment events (out_for_delivery, delivery_attempt_failed, delivered) that are essential to establish the timeline and conflict; missing other ancillary records does not affect correctness. Evidence consistency: the report’s claim of a logical sequence and no contradictory events is fully supported by the three listed events, with no contradictions.

### ORD-189044: score 60

**Failed criteria:** evidence_identification_correct, evidence_consistency_correct

> Cause: the report correctly identifies that the order used a historical address that ended before the order date, matching the ground‑truth scenario. Evidence identification: the agent failed to include the order record containing the order date (and an irrelevant address record), which is essential for establishing the timing of the historical address, so not all required evidence was identified. Evidence consistency: the report’s claim that the historical period ended before the order date is not supported by any listed evidence because the order date is missing, making the reasoning unsupported.

### ORD-189057: score 60

**Failed criteria:** evidence_identification_correct, evidence_consistency_correct

> Cause: the report correctly describes the allocation_failed and backorder_flagged events and the resulting lack of carrier pickup, matching the actual scenario. Evidence identification: the agent omitted essential records such as the order status=processing and an explicit indication that no pickup event occurred, providing only related but incomplete evidence. Evidence consistency: the report’s claims that the order stays in processing and that there is no carrier pickup are not directly supported by the listed evidences, which lack order‑status and explicit no‑pickup evidence.

### ORD-189068: score 60

**Failed criteria:** evidence_identification_correct, evidence_consistency_correct

> Cause: The report correctly states that the order had a label created, no carrier pickup, and that the reservation was released, matching the ground‑truth scenario. Evidence identification: The agent listed the order record, the label_created shipment event, and both inventory events, but omitted the explicit evidence that no pickup event occurred, which is part of the essential supporting evidence. Evidence consistency: The report’s claim that there is no carrier pickup event is not backed by any of the listed evidences (the agent did not provide a record showing the absence of a pickup), so the important claim is unsupported.

