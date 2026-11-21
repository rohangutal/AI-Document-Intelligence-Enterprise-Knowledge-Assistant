"""Structure-preserving chunker for contracts and legal documents."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.ingestion.loaders import DocumentPage


@dataclass(frozen=True)
class LegalChunk:
    chunk_index: int
    content: str
    page_number: int | None
    section_number: str | None
    section_title: str | None
    clause_category: str


_NUMBERED_SECTION = re.compile(r"^\s*(\d+(?:\.\d+)*)(?:[.)])?\s+(.{3,})$")
_CLAUSE_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("termination", ("termination", "terminate", "expiration")),
    ("confidentiality", ("confidential", "non-disclosure", "trade secret")),
    ("indemnification", ("indemnif", "hold harmless")),
    ("limitation_of_liability", ("limitation of liability", "liability")),
    ("payment", ("payment", "invoice", "fees", "compensation")),
    ("intellectual_property", ("intellectual property", "work product", "ownership")),
    ("data_protection", ("personal data", "data protection", "privacy", "gdpr")),
    ("governing_law", ("governing law", "jurisdiction", "venue")),
)


def chunk_legal_document(pages: list[DocumentPage], max_characters: int = 1800) -> list[LegalChunk]:
    """Create chunks that do not cross numbered-section or heading boundaries."""
    if max_characters < 200:
        raise ValueError("max_characters must be at least 200")
    chunks: list[LegalChunk] = []
    current: list[str] = []
    current_page: int | None = None
    section_number: str | None = None
    section_title: str | None = None

    def flush() -> None:
        nonlocal current
        content = "\n".join(current).strip()
        if content:
            chunks.append(
                LegalChunk(
                    chunk_index=len(chunks),
                    content=content,
                    page_number=current_page,
                    section_number=section_number,
                    section_title=section_title,
                    clause_category=classify_clause(content),
                )
            )
        current = []

    for page in pages:
        for raw_line in page.text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            match = _NUMBERED_SECTION.match(line)
            is_heading = bool(match) or (len(line) <= 120 and line.isupper() and len(line.split()) <= 12)
            if is_heading:
                flush()
                if match:
                    section_number, section_title = match.group(1), match.group(2).strip()
                else:
                    section_number, section_title = None, line
                current_page = page.page_number
                current.append(line)
                continue
            if current and sum(len(part) + 1 for part in current) + len(line) > max_characters:
                flush()
            current_page = current_page or page.page_number
            current.append(line)
    flush()
    return chunks


def classify_clause(text: str) -> str:
    lowered = text.lower()
    for category, keywords in _CLAUSE_KEYWORDS:
        if any(keyword in lowered for keyword in keywords):
            return category
    return "other"
