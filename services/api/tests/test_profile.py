from unittest.mock import patch


def test_history_requires_auth(client):
    res = client.get("/v1/profile/history")
    assert res.status_code == 401
    assert res.json()["detail"]["error"]["code"] == "UNAUTHORIZED"


def test_history_returns_user_items(client, db_session):
    from app.db.models import PrescriptionScan, SymptomSubmission, User

    user = User(firebase_uid="test-uid-history", email="test@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    db_session.add(
        SymptomSubmission(
            user_id=user.id,
            inputs={},
            predictions={"items": [{"disease": "Common Cold"}], "confidence_level": "low"},
            model_version="test",
        )
    )
    db_session.add(PrescriptionScan(user_id=user.id, ocr_text="Take Aspirin 75mg"))
    db_session.commit()

    with patch("app.routers.profile.verify_token_required", return_value=user):
        res = client.get("/v1/profile/history", headers={"Authorization": "Bearer fake"})

    assert res.status_code == 200
    items = res.json()["items"]
    types = {i["type"] for i in items}
    assert "symptom" in types
    assert "prescription" in types
    assert any("Common Cold" in i["summary"] for i in items)
