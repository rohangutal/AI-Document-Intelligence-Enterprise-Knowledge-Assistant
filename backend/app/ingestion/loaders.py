"""Safe text extraction for the document formats supported in Phase 4."""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import PurePath


class UnsupportedDocumentType(ValueError):
    """Raised when a file format is not supported by the ingestion pipeline."""


@dataclass(frozen=True)
class DocumentPage:
    page_number: int
    text: str


def load_document(filename: str, content: bytes) -> list[DocumentPage]:
    """Extract text while retaining page boundaries where the format provides them."""
    extension = PurePath(filename).suffix.lower()
    if extension == ".txt":
        return [DocumentPage(1, content.decode("utf-8-sig"))]
    if extension == ".pdf":
        return _load_pdf(content)
    if extension == ".docx":
        return [DocumentPage(1, _load_docx(content))]
    raise UnsupportedDocumentType(f"Unsupported document type: {extension or 'unknown'}")


def _load_pdf(content: bytes) -> list[DocumentPage]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise RuntimeError("PDF ingestion requires the 'pypdf' package") from exc
    reader = PdfReader(BytesIO(content))
    return [DocumentPage(index + 1, page.extract_text() or "") for index, page in enumerate(reader.pages)]


def _load_docx(content: bytes) -> str:
    try:
        from docx import Document
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise RuntimeError("DOCX ingestion requires the 'python-docx' package") from exc
    document = Document(BytesIO(content))
    return "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip())
