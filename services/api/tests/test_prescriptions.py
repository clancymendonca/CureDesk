from unittest.mock import patch

PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


def test_scan_rejects_non_image(client):
    res = client.post(
        "/v1/prescriptions/scan",
        files={"file": ("note.txt", b"hello", "text/plain")},
    )
    assert res.status_code == 400
    assert res.json()["detail"]["error"]["code"] == "INVALID_FILE"


def test_scan_with_mocked_ocr(client):
    matches = [{"brand": "Aspirin", "generic": "acetylsalicylic acid", "confidence": 0.92}]
    with (
        patch("app.routers.prescriptions.extract_text", return_value="Take Aspirin 75mg daily"),
        patch("app.routers.prescriptions.lookup_drugs", return_value=matches),
    ):
        res = client.post(
            "/v1/prescriptions/scan",
            files={"file": ("rx.png", PNG_BYTES, "image/png")},
        )
    assert res.status_code == 200
    data = res.json()
    assert data["ocr_text"] == "Take Aspirin 75mg daily"
    assert data["matches"][0]["brand"] == "Aspirin"


def test_scan_ocr_failure_returns_422(client):
    with patch(
        "app.routers.prescriptions.extract_text", side_effect=ValueError("bad image")
    ):
        res = client.post(
            "/v1/prescriptions/scan",
            files={"file": ("rx.png", PNG_BYTES, "image/png")},
        )
    assert res.status_code == 422
    assert res.json()["detail"]["error"]["code"] == "OCR_FAILED"
