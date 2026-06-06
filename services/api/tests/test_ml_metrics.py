"""ML artifact quality tests."""

import json
from pathlib import Path

import pytest

ARTIFACTS = Path(__file__).resolve().parents[1] / "models" / "artifacts"


def test_metrics_json_exists():
    path = ARTIFACTS / "metrics.json"
    if not path.exists():
        pytest.skip("metrics.json not generated — run ml/train_symptoms.py")
    metrics = json.loads(path.read_text())
    assert metrics.get("n_classes", 0) >= 6
    assert "cv_macro_f1" in metrics
    assert "test_top3_accuracy" in metrics
    assert metrics.get("n_classes_raw", metrics.get("n_classes", 0)) >= 6


def test_model_artifacts_load():
    from app.ml import symptoms as ml

    if not (ARTIFACTS / "symptom_model.joblib").exists():
        pytest.skip("model not trained")
    assert ml.load_artifacts()
    assert ml.is_ready()


def test_predict_returns_confidence(client):
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
        pytest.skip("ML not ready")
    assert res.status_code == 200
    data = res.json()
    assert len(data["predictions"]) <= 3
    assert data["confidence_level"] in ("high", "medium", "low")
    for p in data["predictions"]:
        assert "slug" in p
        assert "disease" in p
