import json

import numpy as np
import joblib
from pathlib import Path

from app.config import settings

_model = None
_preprocessor = None
_label_encoder = None
_disease_classes: list[str] = []
_model_version = "unknown"
_ml_metrics: dict | None = None
_feature_format = "legacy"
_symptom_features: list[str] = []
_legacy_symptom_map: dict[str, list[str]] = {}
_loaded = False


def _artifacts_path(name: str) -> Path:
    return Path(settings.artifacts_dir) / name


def _load_metrics() -> dict | None:
    path = _artifacts_path("metrics.json")
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def load_artifacts() -> bool:
    global _model, _preprocessor, _label_encoder, _disease_classes, _model_version
    global _ml_metrics, _feature_format, _symptom_features, _legacy_symptom_map, _loaded

    model_path = _artifacts_path("symptom_model.joblib")
    prep_path = _artifacts_path("symptom_preprocessor.joblib")
    encoder_path = _artifacts_path("symptom_label_encoder.joblib")
    classes_path = _artifacts_path("disease_classes.json")
    version_path = _artifacts_path("model_version.txt")
    features_path = _artifacts_path("symptom_features.json")
    map_path = _artifacts_path("legacy_symptom_map.json")

    if not model_path.exists() or not prep_path.exists():
        _loaded = False
        return False

    _model = joblib.load(model_path)
    _preprocessor = joblib.load(prep_path)
    _label_encoder = joblib.load(encoder_path) if encoder_path.exists() else None
    if classes_path.exists():
        _disease_classes = json.loads(classes_path.read_text())
    if version_path.exists():
        _model_version = version_path.read_text().strip()
    _ml_metrics = _load_metrics()
    _feature_format = (_ml_metrics or {}).get("feature_format", "legacy")
    if features_path.exists():
        _symptom_features = json.loads(features_path.read_text())
        _feature_format = "wide"
    if map_path.exists():
        _legacy_symptom_map = json.loads(map_path.read_text())
    _loaded = True
    return True


def is_ready() -> bool:
    return _loaded and _model is not None


def get_model_version() -> str:
    return _model_version


def get_symptom_features() -> list[str]:
    path = _artifacts_path("symptom_features.json")
    if path.exists():
        return json.loads(path.read_text())
    return []


def get_feature_format() -> str:
    metrics = _load_metrics() or {}
    return metrics.get("feature_format", "legacy")


def get_ml_metrics() -> dict | None:
    if _ml_metrics is None:
        return _load_metrics()
    return _ml_metrics


def _row_from_request_legacy(data: dict) -> dict:
    def yn(v: bool) -> str:
        return "Yes" if v else "No"

    bp = data["blood_pressure"]
    chol = data["cholesterol_level"]
    return {
        "Fever": yn(data["fever"]),
        "Cough": yn(data["cough"]),
        "Fatigue": yn(data["fatigue"]),
        "Difficulty Breathing": yn(data["difficulty_breathing"]),
        "Age": data["age"],
        "Gender": "Male" if data["gender"] == "male" else "Female",
        "Blood Pressure": bp.capitalize() if bp != "normal" else "Normal",
        "Cholesterol Level": chol.capitalize() if chol != "normal" else "Normal",
    }


def _row_from_request_wide(data: dict) -> dict:
    row = {feat: 0 for feat in _symptom_features}
    extra = data.get("symptoms") or {}
    for feat, val in extra.items():
        if feat in row:
            row[feat] = 1 if val else 0
    symptom_map = _legacy_symptom_map or {
        "fever": ["high_fever", "mild_fever"],
        "cough": ["cough"],
        "fatigue": ["fatigue"],
        "difficulty_breathing": ["breathlessness"],
    }
    for legacy_key, wide_cols in symptom_map.items():
        if legacy_key not in data:
            continue
        if data[legacy_key]:
            for col in wide_cols:
                if col in row:
                    row[col] = 1
    return row


def _row_from_request(data: dict) -> dict:
    if _feature_format == "wide" and _symptom_features:
        return _row_from_request_wide(data)
    return _row_from_request_legacy(data)


def _slugify(name: str) -> str:
    return name.lower().replace(" ", "-").replace("'", "")


def _confidence_level(proba: np.ndarray) -> str:
    sorted_p = np.sort(proba)[::-1]
    top = float(sorted_p[0])
    margin = float(sorted_p[0] - sorted_p[1]) if len(sorted_p) > 1 else top
    if top >= 0.55 and margin >= 0.15:
        return "high"
    if top >= 0.35 and margin >= 0.10:
        return "medium"
    return "low"


def predict_top_k(data: dict, k: int = 3) -> tuple[list[dict], str]:
    if not is_ready():
        raise RuntimeError("ML model not loaded")

    import pandas as pd

    row = _row_from_request(data)
    df = pd.DataFrame([row])
    X = _preprocessor.transform(df)
    proba = _model.predict_proba(X)[0]
    raw_classes = _model.classes_
    if _label_encoder is not None:
        classes = _label_encoder.inverse_transform(raw_classes)
    else:
        classes = raw_classes
    top_idx = np.argsort(proba)[::-1][:k]
    confidence = _confidence_level(proba)

    results = []
    for idx in top_idx:
        disease = classes[idx]
        results.append(
            {
                "disease": disease,
                "slug": _slugify(disease),
                "probability": float(proba[idx]),
            }
        )
    return results, confidence
