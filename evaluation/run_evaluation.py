"""Run the repeatable Phase 8 legal-analysis evaluation suite.

This suite is intentionally transparent and dependency-light. It measures the
deterministic baseline and must not be described as legal accuracy. Production
quality claims require a human-reviewed ground-truth set.
"""

from __future__ import annotations

import json
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.agents.legal_workflow import run_legal_workflow  # noqa: E402
from app.retrieval.hybrid import hybrid_search  # noqa: E402
from app.services.legal_analysis import extract_clauses  # noqa: E402


DATASET = Path(__file__).parent / "datasets" / "legal_eval.json"
REPORT_DIR = Path(__file__).parent / "reports"


def _write_report(name: str, content: str) -> Path:
    """Write reports, falling back for read-only checkouts used in CI."""
    try:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        destination = REPORT_DIR / name
        destination.write_text(content, encoding="utf-8")
        return destination
    except PermissionError:
        fallback = Path(tempfile.gettempdir()) / "legal_eval_reports"
        fallback.mkdir(parents=True, exist_ok=True)
        destination = fallback / name
        destination.write_text(content, encoding="utf-8")
        return destination


def _f1(precision: float, recall: float) -> float:
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def _retrieval_metrics(case: dict[str, Any], state: dict[str, Any]) -> dict[str, float]:
    expected = set(case.get("expected_retrieved_chunk_ids", []))
    actual = [str(item.get("chunk_id")) for item in state.get("retrieved", [])]
    actual_set = set(actual)
    true_positive = len(expected & actual_set)
    precision = true_positive / len(actual_set) if actual_set else 0.0
    recall = true_positive / len(expected) if expected else 1.0
    reciprocal_rank = next((1 / (index + 1) for index, value in enumerate(actual) if value in expected), 0.0)
    return {"precision_at_k": precision, "recall_at_k": recall, "mrr": reciprocal_rank}


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    task = case["task"]
    if task == "question":
        state = run_legal_workflow(task=task, question=case["question"], chunks=case["chunks"])
        retrieval = _retrieval_metrics(case, state)
        citations = " ".join(state.get("citations", []))
        citation_correct = all(term in citations for term in case.get("expected_citation_terms", []))
        evidence_valid = bool(state.get("evidence_valid"))
        return {"id": case["id"], "task": task, **retrieval, "citation_correct": citation_correct, "evidence_valid": evidence_valid, "evidence_valid_check": evidence_valid == case.get("expected_evidence_valid", True)}
    if task == "risk":
        state = run_legal_workflow(task=task, document_text=case["document_text"])
        severities = [risk["severity"] for risk in state.get("risks", [])]
        terms = " ".join(str(risk.get("clause", "")) for risk in state.get("risks", [])).lower()
        expected_severities = Counter(case.get("expected_risk_severities", []))
        actual_severities = Counter(severities)
        matched = sum((expected_severities & actual_severities).values())
        precision = matched / len(severities) if severities else 0.0
        recall = matched / len(case.get("expected_risk_severities", [])) if case.get("expected_risk_severities") else 1.0
        evidence_valid = bool(state.get("evidence_valid"))
        return {"id": case["id"], "task": task, "risk_precision": precision, "risk_recall": recall, "risk_f1": _f1(precision, recall), "expected_terms_present": all(term in terms for term in case.get("expected_risk_terms", [])), "evidence_valid": evidence_valid, "evidence_valid_check": evidence_valid == case.get("expected_evidence_valid", False)}
    if task == "obligation":
        clauses = extract_clauses(case["document_text"])
        actual = sum(len(clause["obligations"]) for clause in clauses)
        expected = case["expected_obligation_count"]
        return {"id": case["id"], "task": task, "obligation_count": actual, "expected_obligation_count": expected, "count_match": actual == expected}
    raise ValueError(f"Unsupported evaluation task: {task}")


def run() -> dict[str, Any]:
    cases = json.loads(DATASET.read_text(encoding="utf-8"))
    results = [evaluate_case(case) for case in cases]
    check_keys = {"citation_correct", "expected_terms_present", "count_match"}
    bool_metrics = [
        value
        for result in results
        for key, value in result.items()
        if isinstance(value, bool) and (key.endswith("_check") or key in check_keys)
    ]
    summary = {
        "case_count": len(results),
        "passed_boolean_checks": sum(bool_metrics),
        "boolean_check_count": len(bool_metrics),
        "pass_rate": sum(bool_metrics) / len(bool_metrics) if bool_metrics else 0.0,
        "limitations": [
            "The dataset is a deterministic smoke/evaluation baseline, not legal ground truth.",
            "Faithfulness and answer relevance require human review or a separately validated judge.",
            "Risk severity quality must be assessed against reviewed annotations before production claims.",
        ],
        "results": results,
    }
    report_paths = [_write_report("legal_eval.json", json.dumps(summary, indent=2) + "\n")]
    lines = ["# Phase 8 Legal Evaluation Report", "", f"- Cases: {summary['case_count']}", f"- Boolean checks passed: {summary['passed_boolean_checks']}/{summary['boolean_check_count']}", f"- Baseline pass rate: {summary['pass_rate']:.1%}", "", "## Interpretation", "", "This is an automated deterministic baseline. It is not a claim of legal accuracy. Human-reviewed annotations are required for legal-analysis quality, faithfulness, and severity evaluation.", "", "## Case results", ""]
    for result in results:
        lines.append(f"### {result['id']} ({result['task']})")
        for key, value in result.items():
            if key not in {"id", "task"}:
                lines.append(f"- {key}: {value}")
        lines.append("")
    report_paths.append(_write_report("legal_eval.md", "\n".join(lines)))
    summary["report_paths"] = [str(path) for path in report_paths]
    return summary


if __name__ == "__main__":
    result = run()
    print(json.dumps({key: result[key] for key in ("case_count", "passed_boolean_checks", "boolean_check_count", "pass_rate")}, indent=2))
