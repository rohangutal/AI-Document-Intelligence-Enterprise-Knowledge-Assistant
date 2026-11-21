from app.services.legal_analysis import compare_documents, extract_clauses, retrieve_chunks


def test_extract_clauses_returns_risk_and_obligation_signals() -> None:
    clauses = extract_clauses(
        "Confidentiality\n\nThe receiving party shall protect confidential information.\n\n"
        "The supplier has unlimited liability for all losses."
    )

    assert len(clauses) == 3
    assert clauses[0]["clause_type"] == "confidentiality"
    assert clauses[1]["obligations"]
    assert clauses[2]["risk_level"] == "high"


def test_compare_documents_reports_replacement() -> None:
    result = compare_documents("Payment is due in 30 days.", "Payment is due in 15 days.")

    assert result["changed"] is True
    assert result["additions"] == 1
    assert result["deletions"] == 1
    assert result["changes"][0]["change_type"] == "replace"


def test_retrieve_chunks_preserves_source_citation() -> None:
    result = retrieve_chunks(
        "termination notice",
        [
            {"chunk_id": "c-1", "content": "Termination requires 30 days notice.", "page_number": 4, "section_title": "Termination"},
            {"chunk_id": "c-2", "content": "Invoices are payable monthly.", "page_number": 2, "section_title": "Payment"},
        ],
        top_k=1,
    )

    assert len(result) == 1
    assert result[0]["chunk_id"] == "c-1"
    assert result[0]["citation"] == "Source document — Page 4 — Section Termination — Chunk c-1"
