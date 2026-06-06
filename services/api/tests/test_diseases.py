def test_list_diseases_empty(client):
    res = client.get("/v1/diseases")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 0
