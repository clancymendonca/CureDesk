def test_predict_symptoms(client):
    payload = {
        "fever": True,
        "cough": True,
        "fatigue": False,
        "difficulty_breathing": False,
        "age": 30,
        "gender": "female",
        "blood_pressure": "normal",
        "cholesterol_level": "normal",
    }
    res = client.post("/v1/symptoms/predict", json=payload)
    if res.status_code == 503:
        assert res.json()["detail"]["error"]["code"] == "ML_NOT_READY"
    else:
        assert res.status_code == 200
        data = res.json()
        assert "predictions" in data
        assert "model_version" in data
        assert len(data["predictions"]) <= 3


def test_symptom_features_endpoint(client):
    res = client.get("/v1/symptoms/features")
    if res.status_code == 503:
        assert res.json()["detail"]["error"]["code"] == "ML_NOT_READY"
    elif res.status_code == 404:
        assert res.json()["detail"]["error"]["code"] == "NO_FEATURES"
    else:
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data["features"], list)
        assert data["features"]
        assert "model_version" in data
        assert "feature_format" in data
