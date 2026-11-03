# Agent Evaluation Report

- **Run ID:** `d6ffa554-8196-40a7-92e3-ef6efadf60b1`
- **Generated:** 2026-11-03 15:43:47 UTC
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
| Average overall score | 94.3 |
| Lowest / highest score | 20 / 100 |

## Score Distribution

| Overall score | Cases |
|---:|---:|
| 100 | 62 |
| 80 | 4 |
| 20 | 4 |

## Criterion Pass Rates

| Criterion | Passed | Rate |
|---|---:|---:|
| cause_correct | 66/70 | 94.3% |
| evidence_consistency_correct | 66/70 | 94.3% |

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
| ORD-189010 | 100 | PASS |
| ORD-189011 | 100 | PASS |
| ORD-189012 | 100 | PASS |
| ORD-189013 | 100 | PASS |
| ORD-189014 | 100 | PASS |
| ORD-189015 | 100 | PASS |
| ORD-189016 | 100 | PASS |
| ORD-189017 | 100 | PASS |
| ORD-189018 | 100 | PASS |
| ORD-189019 | 100 | PASS |
| ORD-189020 | 100 | PASS |
| ORD-189021 | 100 | PASS |
| ORD-189022 | 100 | PASS |
| ORD-189023 | 100 | PASS |
| ORD-189024 | 100 | PASS |
| ORD-189025 | 100 | PASS |
| ORD-189026 | 100 | PASS |
| ORD-189027 | 100 | PASS |
| ORD-189028 | 100 | PASS |
| ORD-189029 | 100 | PASS |
| ORD-189030 | 100 | PASS |
| ORD-189031 | 80 | PASS |
| ORD-189032 | 80 | PASS |
| ORD-189033 | 100 | PASS |
| ORD-189034 | 80 | PASS |
| ORD-189035 | 100 | PASS |
| ORD-189036 | 100 | PASS |
| ORD-189037 | 100 | PASS |
| ORD-189038 | 20 | FAIL |
| ORD-189039 | 100 | PASS |
| ORD-189040 | 100 | PASS |
| ORD-189041 | 100 | PASS |
| ORD-189042 | 100 | PASS |
| ORD-189043 | 100 | PASS |
| ORD-189044 | 20 | FAIL |
| ORD-189045 | 100 | PASS |
| ORD-189046 | 20 | FAIL |
| ORD-189047 | 100 | PASS |
| ORD-189048 | 100 | PASS |
| ORD-189049 | 100 | PASS |
| ORD-189050 | 100 | PASS |
| ORD-189051 | 100 | PASS |
| ORD-189052 | 100 | PASS |
| ORD-189053 | 20 | FAIL |
| ORD-189054 | 100 | PASS |
| ORD-189055 | 80 | PASS |
| ORD-189056 | 100 | PASS |
| ORD-189057 | 100 | PASS |
| ORD-189058 | 100 | PASS |
| ORD-189059 | 100 | PASS |
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

### ORD-189038: score 20

**Failed criteria:** cause_correct

> Cause: The report attributes the delivery issue to an entrance being inaccessible and a later successful attempt, whereas the ground truth states the issue stemmed from an apparent conflict due to misordered events (return to station then redispatch). The identified cause does not match the actual scenario. Evidence consistency: All factual statements in the report (failed attempt at 12:30, second out‑for‑delivery, successful delivery at 18:20) are directly supported by the listed shipment events, and no contradictions are present.

### ORD-189044: score 20

**Failed criteria:** cause_correct

> Cause: The report says the issue is that the delivery address is outdated, but the ground truth states the cause is that the destination matches a previously recorded address whose validity ended long before the order, which is essentially the same reason. However, the report frames it as an unexplained mismatch without identifying the specific cause that the system used an expired address record, so it does not correctly pinpoint the actual cause. Evidence: All factual statements in the report are directly supported by the listed upfront and tool evidence items.

### ORD-189046: score 20

**Failed criteria:** cause_correct

> Cause: The report states the cause is unknown, saying no record explains why the outdated address was used, which does not match the ground truth that the cause is the use of an outdated address that was still in the system (i.e., the system used the older address). The  

### ORD-189053: score 20

**Failed criteria:** cause_correct

> Cause: The report states the delivery address was outdated and "no records explain why the outdated address was used," implying the cause is unknown. The ground truth indicates the cause is that the order used a previously recorded address whose validity had expired, i.e., the system ... (...)

