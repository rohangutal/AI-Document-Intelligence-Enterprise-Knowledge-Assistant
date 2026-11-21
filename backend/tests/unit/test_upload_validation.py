from app.api.v1.endpoints.contracts import _MIME_TYPES


def test_upload_supports_only_document_extensions() -> None:
    assert set(_MIME_TYPES) == {".pdf", ".docx", ".txt"}
