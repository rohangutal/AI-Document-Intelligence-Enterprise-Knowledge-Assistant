from fastapi.testclient import TestClient

from app.main import app


def test_health_check_returns_service_status() -> None:
    response = TestClient(app).get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "Enterprise AI Knowledge Assistant"
    assert "timestamp" in payload


def test_security_headers_are_present() -> None:
    response = TestClient(app).get("/api/v1/health")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
