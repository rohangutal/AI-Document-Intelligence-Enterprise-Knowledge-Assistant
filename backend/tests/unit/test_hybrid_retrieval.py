from app.retrieval.hybrid import hybrid_search


def test_hybrid_search_ranks_matching_clause_and_returns_citation() -> None:
    results = hybrid_search(
        "termination notice",
        [
            {
                "chunk_id": "c-1",
                "document_name": "Vendor_Agreement.pdf",
                "content": "Termination requires thirty days written notice.",
                "page_number": 8,
                "section_number": "12.2",
                "embedding": [1.0, 0.0],
            },
            {
                "chunk_id": "c-2",
                "document_name": "Vendor_Agreement.pdf",
                "content": "Invoices are payable monthly.",
                "page_number": 4,
                "section_number": "5.1",
                "embedding": [0.0, 1.0],
            },
        ],
        query_embedding=[1.0, 0.0],
        top_k=1,
    )

    assert [result["chunk_id"] for result in results] == ["c-1"]
    assert "Page 8" in results[0]["citation"]
    assert "12.2" in results[0]["citation"]


def test_hybrid_search_applies_metadata_filter() -> None:
    results = hybrid_search(
        "payment",
        [
            {"chunk_id": "nda", "content": "Payment details", "contract_type": "nda"},
            {"chunk_id": "msa", "content": "Payment details", "contract_type": "msa"},
        ],
        metadata_filters={"contract_type": "msa"},
    )

    assert [result["chunk_id"] for result in results] == ["msa"]
