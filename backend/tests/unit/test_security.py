from uuid import uuid4

from app.core.security import create_access_token, hash_password, verify_password


def test_password_hash_is_not_reversible_and_verifies() -> None:
    encoded = hash_password("correct horse battery staple")

    assert encoded.startswith("scrypt$")
    assert verify_password("correct horse battery staple", encoded) is True
    assert verify_password("wrong password", encoded) is False


def test_access_token_requires_configured_secret(monkeypatch) -> None:
    from app.core.config import get_settings

    get_settings.cache_clear()
    monkeypatch.delenv("JWT_SECRET", raising=False)
    try:
        create_access_token(uuid4())
    except RuntimeError as exc:
        assert "JWT_SECRET" in str(exc)
    else:
        raise AssertionError("Token creation should require JWT_SECRET")
