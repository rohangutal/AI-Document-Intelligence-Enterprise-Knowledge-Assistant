"""Deterministic legal-analysis primitives used before an LLM is configured.

These functions deliberately return source offsets and citations so an LLM or
agent can later use them as grounded tools instead of inventing evidence.
"""

from __future__ import annotations

import difflib
import re

from app.retrieval.hybrid import hybrid_search


_CLAUSE_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("termination", ("termination", "terminate", "expiration")),
    ("confidentiality", ("confidential", "non-disclosure", "trade secret")),
    ("indemnification", ("indemnif", "hold harmless")),
    ("limitation_of_liability", ("limitation of liability", "liable", "liability")),
    ("governing_law", ("governing law", "jurisdiction", "venue")),
    ("payment", ("payment", "invoice", "fees", "compensation")),
    ("intellectual_property", ("intellectual property", "work product", "ownership")),
    ("data_protection", ("personal data", "data protection", "privacy", "gdpr")),
    ("auto_renewal", ("automatically renew", "auto-renew", "renewal")),
)

_RISK_RULES: tuple[tuple[str, str, str], ...] = (
    ("high", "unlimited liability", "Unlimited or uncapped liability."),
    ("high", "sole discretion", "A party may act without an objective standard."),
    ("high", "personal guarantee", "A personal guarantee creates individual exposure."),
    ("medium", "automatically renew", "The agreement may renew without an explicit action."),
    ("medium", "auto-renew", "The agreement may renew without an explicit action."),
    ("medium", "30 days", "A short notice or cure period may limit response time."),
    ("medium", "indemnif", "Indemnification scope should be reviewed."),
)


def _clause_type(text: str) -> str:
    lowered = text.lower()
    for clause_type, keywords in _CLAUSE_PATTERNS:
        if any(keyword in lowered for keyword in keywords):
            return clause_type
    return "other"


def _risk(text: str) -> tuple[str, list[str]]:
    lowered = text.lower()
    reasons = [reason for level, keyword, reason in _RISK_RULES if keyword in lowered]
    if any(level == "high" and keyword in lowered for level, keyword, _ in _RISK_RULES):
        return "high", reasons
    if reasons:
        return "medium", reasons
    return "low", []


def _obligations(text: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [sentence.strip() for sentence in sentences if re.search(r"\b(shall|must|required to|agrees to|will)\b", sentence, re.I)]


def extract_clauses(text: str) -> list[dict[str, object]]:
    """Split text into paragraph clauses and annotate likely legal signals."""
    blocks = [match for match in re.finditer(r"\S(?:.*?\S)?(?=\n\s*\n|\Z)", text, re.S)]
    if not blocks:
        blocks = [match for match in re.finditer(r".+", text)]
    results = []
    for match in blocks:
        content = match.group().strip()
        if not content:
            continue
        risk_level, risk_reasons = _risk(content)
        title = content.splitlines()[0].strip() if "\n" in content else None
        results.append(
            {
                "clause_type": _clause_type(content),
                "title": title,
                "text": content,
                "source_start": match.start(),
                "source_end": match.end(),
                "risk_level": risk_level,
                "risk_reasons": risk_reasons,
                "obligations": _obligations(content),
            }
        )
    return results


def compare_documents(original: str, revised: str) -> dict[str, object]:
    original_lines, revised_lines = original.splitlines(), revised.splitlines()
    changes: list[dict[str, str | None]] = []
    additions = deletions = 0
    for tag, old_start, old_end, new_start, new_end in difflib.SequenceMatcher(None, original_lines, revised_lines).get_opcodes():
        if tag == "equal":
            continue
        old = "\n".join(original_lines[old_start:old_end]) or None
        new = "\n".join(revised_lines[new_start:new_end]) or None
        if tag in ("delete", "replace"):
            deletions += old_end - old_start
        if tag in ("insert", "replace"):
            additions += new_end - new_start
        changes.append({"change_type": tag, "original": old, "revised": new})
    return {"changed": bool(changes), "additions": additions, "deletions": deletions, "changes": changes}


_EXPECTED_CLAUSES: dict[str, tuple[str, ...]] = {
    "nda": ("confidentiality", "termination", "governing_law", "indemnification", "intellectual_property", "data_protection"),
    "employment": ("payment", "confidentiality", "intellectual_property", "termination", "governing_law", "dispute_resolution"),
    "msa": ("payment", "termination", "indemnification", "limitation_of_liability", "confidentiality", "intellectual_property", "data_protection"),
    "service": ("payment", "termination", "indemnification", "limitation_of_liability", "confidentiality", "intellectual_property"),
}


def compare_contracts(original: str, revised: str) -> dict[str, object]:
    """Compare clause blocks by legal category and text similarity."""
    original_clauses = extract_clauses(original)
    revised_clauses = extract_clauses(revised)
    unmatched_revised = set(range(len(revised_clauses)))
    clause_changes: list[dict[str, object]] = []
    for old in original_clauses:
        candidates = [(index, new, _clause_similarity(str(old["text"]), str(new["text"]))) for index, new in enumerate(revised_clauses) if index in unmatched_revised and new["clause_type"] == old["clause_type"]]
        if not candidates:
            clause_changes.append({"clause_type": old["clause_type"], "change_type": "removed", "original": old["text"], "revised": None})
            continue
        index, new, similarity = max(candidates, key=lambda item: item[2])
        unmatched_revised.remove(index)
        change_type = "unchanged" if similarity == 1.0 else "modified"
        clause_changes.append({"clause_type": old["clause_type"], "change_type": change_type, "original": old["text"], "revised": new["text"], "similarity": round(similarity, 4)})
    for index in sorted(unmatched_revised):
        new = revised_clauses[index]
        clause_changes.append({"clause_type": new["clause_type"], "change_type": "added", "original": None, "revised": new["text"]})
    return {**compare_documents(original, revised), "clause_changes": clause_changes, "modified_clauses": sum(item["change_type"] == "modified" for item in clause_changes)}


def missing_clause_checks(text: str, contract_type: str) -> list[dict[str, object]]:
    """Return review items for expected clauses absent from a contract."""
    detected = {str(clause["clause_type"]) for clause in extract_clauses(text)}
    expected = _EXPECTED_CLAUSES.get(contract_type.lower(), ())
    return [{"clause_type": clause_type, "status": "present" if clause_type in detected else "missing", "requires_review": clause_type not in detected} for clause_type in expected]


def summarize_contract(text: str, contract_type: str | None = None) -> dict[str, object]:
    """Build a structured, source-preserving summary without legal conclusions."""
    clauses = extract_clauses(text)
    dates = re.findall(r"\b(?:\d{1,2}[/-]){2}\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b", text)
    parties = re.findall(r"(?:between|by and among)\s+([^.;]+)", text, re.I)
    risks = [clause for clause in clauses if clause["risk_level"] != "low"]
    obligations = [obligation for clause in clauses for obligation in clause["obligations"]]
    return {"contract_type": contract_type, "parties": parties[:5], "dates": dates, "clause_count": len(clauses), "risk_count": len(risks), "obligation_count": len(obligations), "key_clauses": [{"type": clause["clause_type"], "text": clause["text"]} for clause in clauses], "review_notice": "This summary is informational and requires qualified professional review."}


def _clause_similarity(original: str, revised: str) -> float:
    return difflib.SequenceMatcher(None, " ".join(original.lower().split()), " ".join(revised.lower().split())).ratio()


def retrieve_chunks(
    query: str,
    chunks: list[dict[str, object]],
    top_k: int,
    *,
    similarity_threshold: float = 0.0,
    metadata_filters: dict[str, object] | None = None,
) -> list[dict[str, object]]:
    return hybrid_search(
        query,
        chunks,
        top_k=top_k,
        similarity_threshold=similarity_threshold,
        metadata_filters=metadata_filters,
    )

