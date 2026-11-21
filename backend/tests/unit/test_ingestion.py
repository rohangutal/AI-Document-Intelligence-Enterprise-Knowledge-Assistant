from app.ingestion.legal_chunker import chunk_legal_document
from app.ingestion.loaders import DocumentPage, UnsupportedDocumentType, load_document


def test_text_loader_preserves_content() -> None:
    pages = load_document("agreement.txt", "1. Termination\nThe party shall provide notice.".encode())

    assert pages == [DocumentPage(1, "1. Termination\nThe party shall provide notice.")]


def test_loader_rejects_unknown_extension() -> None:
    try:
        load_document("agreement.rtf", b"text")
    except UnsupportedDocumentType as exc:
        assert ".rtf" in str(exc)
    else:
        raise AssertionError("Unsupported document type was accepted")


def test_legal_chunker_preserves_section_metadata() -> None:
    chunks = chunk_legal_document(
        [
            DocumentPage(
                3,
                "1. Termination\nThe customer may terminate this Agreement on thirty days notice.\n\n"
                "2. Payment\nInvoices are payable within thirty days.",
            )
        ]
    )

    assert len(chunks) == 2
    assert chunks[0].section_number == "1"
    assert chunks[0].section_title == "Termination"
    assert chunks[0].page_number == 3
    assert chunks[0].clause_category == "termination"
    assert chunks[1].clause_category == "payment"
