# Phase 8 Legal Evaluation Report

- Cases: 3
- Boolean checks passed: 5/5
- Baseline pass rate: 100.0%

## Interpretation

This is an automated deterministic baseline. It is not a claim of legal accuracy. Human-reviewed annotations are required for legal-analysis quality, faithfulness, and severity evaluation.

## Case results

### termination-citation-001 (question)

- precision_at_k: 0.5
- recall_at_k: 1.0
- mrr: 0.5
- citation_correct: True
- evidence_valid: True
- evidence_valid_check: True

### risk-detection-001 (risk)

- risk_precision: 1.0
- risk_recall: 1.0
- risk_f1: 1.0
- expected_terms_present: True
- evidence_valid: False
- evidence_valid_check: True

The risk result correctly remains evidence-invalid because the test intentionally supplies no page/chunk source evidence.

### obligation-extraction-001 (obligation)

- obligation_count: 2
- expected_obligation_count: 2
- count_match: True

## Findings

- Retrieval recall and citation construction pass this baseline, but precision is reduced by a payment distractor in the top-k set.
- Risk grouping is clause-level; multiple signals in one paragraph are represented as one review item.
- Evidence validation correctly warns when risk analysis lacks chunk-level source evidence.
- Human-reviewed ground truth and authenticated integration/security tests are still required before production quality claims.
