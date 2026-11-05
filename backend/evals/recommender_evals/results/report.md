# Recommender Evaluation Report

- **Run ID:** `test-run`
- **Generated:** 2026-11-05 11:18:25 UTC
- **Judge model:** test-model

## Overall Result

**PASS**: 67/69 recommendations passed (97.10%). Required: at least 63/69 (90%).

| Metric | Value |
|---|---:|
| Total cases | 69 |
| Passed (score >= 90.0) | 67 |
| Failed | 2 |
| of which errored | 0 |
| Pass rate | 97.10% |
| Average overall score | 95.4 |
| Lowest / highest score | 0 / 100 |

## Score Distribution

| Overall score | Cases |
|---:|---:|
| 100 | 61 |
| 80 | 6 |
| 0 | 2 |

## Criterion Pass Rates

| Criterion | Passed | Rate |
|---|---:|---:|
| recommendation_correct | 67/69 | 97.1% |
| evidence_consistency_correct | 61/69 | 88.4% |

## Individual Results

| Case ID | Score | Result |
|---|---:|---|
| ORD-189001 | 100 | PASS |
| ORD-189002 | 80 | PASS |
| ORD-189003 | 0 | FAIL |
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
| ORD-189019 | 80 | PASS |
| ORD-189020 | 100 | PASS |
| ORD-189021 | 80 | PASS |
| ORD-189022 | 100 | PASS |
| ORD-189023 | 100 | PASS |
| ORD-189024 | 100 | PASS |
| ORD-189025 | 100 | PASS |
| ORD-189026 | 100 | PASS |
| ORD-189027 | 100 | PASS |
| ORD-189028 | 100 | PASS |
| ORD-189029 | 100 | PASS |
| ORD-189030 | 100 | PASS |
| ORD-189031 | 0 | FAIL |
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
| ORD-189057 | 100 | PASS |
| ORD-189058 | 100 | PASS |
| ORD-189059 | 100 | PASS |
| ORD-189060 | 100 | PASS |
| ORD-189061 | 100 | PASS |
| ORD-189062 | 100 | PASS |
| ORD-189063 | 80 | PASS |
| ORD-189064 | 100 | PASS |
| ORD-189065 | 100 | PASS |
| ORD-189066 | 100 | PASS |
| ORD-189067 | 100 | PASS |
| ORD-189068 | 100 | PASS |
| ORD-189069 | 80 | PASS |
| ORD-189070 | 80 | PASS |

## Failed Recommendations

### ORD-189003: score 0

**Failed criteria:** recommendation_correct, evidence_consistency_correct

> The policy states that a carrier trace request should be made when tracking is unchanged for 5+ business days, which the recommendation follows. However, escalation to a senior operator is only required when specific conditions apply, such as the shipment being more than 7 days past its ship date (or other listed triggers). The case provides no evidence that the shipment exceeds 7 days since shipping, so escalating is not justified and violates the policy. The cited evidence does exist in the policy, but the escalation rule is misapplied because its condition is not met, so the evidence does not support the recommended escalation. Hence both the recommendation and the evidence usage are incorrect.

### ORD-189031: score 0

**Failed criteria:** recommendation_correct, evidence_consistency_correct

> The policy permits a carrier trace request only after 5 business days without a tracking update and escalation to a senior operator only when specific triggers (e.g., shipment >7 days past ship date) apply. The recommendation escalates and requests a trace without showing that either condition is satisfied, so it does not clearly comply with the policy. Both cited policy statements exist verbatim in the company policy, but they are conditional; the recommendation presents the actions as unconditional, so the evidence does not adequately justify the suggested steps. Hence both criteria are evaluated as incorrect.

