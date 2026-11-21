from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "evaluation"))

from run_evaluation import evaluate_case  # noqa: E402


def test_question_evaluation_checks_citation_grounding() -> None:
    result = evaluate_case(
        {
            "id": "question",
            "task": "question",
            "question": "What are the termination conditions?",
            "chunks": [{"chunk_id": "c-1", "document_name": "Vendor.pdf", "content": "Either party may terminate for cause.", "page_number": 8, "section_number": "12.2"}],
            "expected_retrieved_chunk_ids": ["c-1"],
            "expected_citation_terms": ["Vendor.pdf", "Page 8", "12.2"],
        }
    )

    assert result["precision_at_k"] == 1.0
    assert result["recall_at_k"] == 1.0
    assert result["citation_correct"] is True
