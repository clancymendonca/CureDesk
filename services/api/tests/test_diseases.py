def test_list_diseases_empty(client):
    res = client.get("/v1/diseases")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 0


def test_disease_list_and_detail_with_seeded_data(client, db_session):
    from app.db.models import Disease

    disease = Disease(
        slug="test-malaria",
        name="Test Malaria",
        description="A mosquito-borne infectious disease.",
        common_symptoms={"fever": 0.9},
    )
    db_session.add(disease)
    db_session.commit()
    try:
        res = client.get("/v1/diseases", params={"q": "test malaria"})
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 1
        assert data["items"][0]["slug"] == "test-malaria"

        res = client.get("/v1/diseases/test-malaria")
        assert res.status_code == 200
        detail = res.json()
        assert detail["name"] == "Test Malaria"
        assert detail["common_symptoms"] == {"fever": 0.9}
    finally:
        db_session.delete(disease)
        db_session.commit()


def test_disease_detail_404(client):
    res = client.get("/v1/diseases/does-not-exist")
    assert res.status_code == 404
    assert res.json()["detail"]["error"]["code"] == "NOT_FOUND"
