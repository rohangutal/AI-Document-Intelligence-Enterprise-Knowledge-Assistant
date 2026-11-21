from app.db.base import Base
from app.models import entities  # noqa: F401 - registers all mapped entities


def test_legal_domain_tables_are_registered() -> None:
    expected = {
        "contracts",
        "contract_parties",
        "extracted_clauses",
        "contract_risks",
        "contract_obligations",
        "contract_versions",
        "clause_comparisons",
        "missing_clause_checks",
        "risk_review_history",
    }

    assert expected.issubset(Base.metadata.tables)


def test_contract_risk_and_obligation_cascade_foreign_keys_exist() -> None:
    risk = Base.metadata.tables["contract_risks"]
    obligation = Base.metadata.tables["contract_obligations"]

    assert any(fk.ondelete == "CASCADE" for fk in risk.foreign_keys)
    assert any(fk.ondelete == "CASCADE" for fk in obligation.foreign_keys)
