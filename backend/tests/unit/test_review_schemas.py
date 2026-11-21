import pytest
from pydantic import ValidationError

from app.schemas.review import ObligationUpdate, RiskReviewRequest


def test_review_statuses_are_limited_to_human_workflow_values() -> None:
    assert RiskReviewRequest(status="under_review").status == "under_review"
    with pytest.raises(ValidationError):
        RiskReviewRequest(status="legally_invalid")


def test_obligation_update_allows_partial_updates() -> None:
    update = ObligationUpdate(status="completed")

    assert update.model_dump(exclude_unset=True) == {"status": "completed"}
