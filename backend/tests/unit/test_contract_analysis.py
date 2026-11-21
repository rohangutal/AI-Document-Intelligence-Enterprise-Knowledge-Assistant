from app.services.legal_analysis import compare_contracts, missing_clause_checks, summarize_contract


def test_compare_contracts_matches_modified_clauses_by_category() -> None:
    result = compare_contracts(
        "1. Termination\nEither party may terminate on 30 days notice.\n\n2. Payment\nNet 30.",
        "1. Termination\nEither party may terminate on 90 days notice.\n\n2. Payment\nNet 30.",
    )
    changes = {item["clause_type"]: item["change_type"] for item in result["clause_changes"]}
    assert changes["termination"] == "modified"
    assert changes["payment"] == "unchanged"
    assert result["modified_clauses"] == 1


def test_missing_clause_checklist_is_review_oriented() -> None:
    checks = missing_clause_checks("Confidentiality\nThe parties shall keep information confidential.", "nda")
    assert {item["clause_type"] for item in checks} >= {"confidentiality", "termination"}
    termination = next(item for item in checks if item["clause_type"] == "termination")
    assert termination["status"] == "missing"
    assert termination["requires_review"] is True


def test_summary_distinguishes_review_notice() -> None:
    summary = summarize_contract("The parties agree to payment of $10,000 on 2026-01-15.", "service")
    assert summary["contract_type"] == "service"
    assert "2026-01-15" in summary["dates"]
    assert "professional review" in summary["review_notice"]
