# Phase 8 Evaluation

This directory contains the repeatable evaluation baseline for retrieval,
grounding, citations, risk detection, and obligation extraction.

Run it from the repository root:

```powershell
python .\evaluation\run_evaluation.py
```

Outputs:

- `reports/legal_eval.json` — machine-readable metrics.
- `reports/legal_eval.md` — human-readable report.

The included dataset is a deterministic smoke/evaluation baseline. It is not
legal ground truth and must not be used to claim legal accuracy. Before
production use, add human-reviewed annotations for clause spans, clause types,
risk categories/severity, obligations, dates, citations, faithfulness, and
answer relevance. Security tests remain in `backend/tests/unit` and should be
extended with authenticated integration tests against an isolated database.
