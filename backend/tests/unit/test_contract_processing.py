from app.services.contract_processing import analyze_persisted_contract


def test_analysis_service_is_exposed() -> None:
    assert callable(analyze_persisted_contract)
