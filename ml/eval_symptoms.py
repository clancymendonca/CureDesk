#!/usr/bin/env python3
"""Evaluate symptom model and run sample inference."""

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT.parent / "services" / "api" / "models" / "artifacts"
DATA = ROOT / "data" / "symptoms" / "Disease_symptom_and_patient_profile_dataset.csv"
FEATURES = [
    "Fever",
    "Cough",
    "Fatigue",
    "Difficulty Breathing",
    "Age",
    "Gender",
    "Blood Pressure",
    "Cholesterol Level",
]


def main() -> None:
    model_path = ARTIFACTS / "symptom_model.joblib"
    prep_path = ARTIFACTS / "symptom_preprocessor.joblib"
    metrics_path = ARTIFACTS / "metrics.json"

    if metrics_path.exists():
        metrics = json.loads(metrics_path.read_text())
        print("=== metrics.json ===")
        print(f"  model: {metrics.get('model_version')}")
        print(f"  classes: {metrics.get('n_classes')} (trained), {metrics.get('n_classes_raw', 'n/a')} (dataset)")
        print(f"  cv_macro_f1: {metrics.get('cv_macro_f1', 0):.3f}")
        print(f"  cv_top3: {metrics.get('cv_top3_accuracy', 0):.2%}")
        print(f"  test_accuracy: {metrics.get('test_accuracy', 0):.2%}")
        print(f"  test_top3: {metrics.get('test_top3_accuracy', 0):.2%}")

    if not model_path.exists() or not prep_path.exists():
        raise SystemExit("Model artifacts not found. Run: python ml/train_symptoms.py")

    model = joblib.load(model_path)
    prep = joblib.load(prep_path)
    encoder_path = ARTIFACTS / "symptom_label_encoder.joblib"
    label_encoder = joblib.load(encoder_path) if encoder_path.exists() else None

    if DATA.exists():
        df = pd.read_csv(DATA)
        if label_encoder is not None:
            known = set(label_encoder.classes_)
            df_eval = df[df["Disease"].isin(known)]
            skipped = len(df) - len(df_eval)
            if skipped:
                print(f"\nEval on {len(df_eval)} rows ({skipped} rows skipped — rare classes excluded from model)")
        else:
            df_eval = df

        X = prep.transform(df_eval[FEATURES])
        y_str = df_eval["Disease"]
        if label_encoder is not None:
            y = label_encoder.transform(y_str)
            classes = label_encoder.classes_
        else:
            y = y_str
            classes = model.classes_

        y_pred = model.predict(X)
        acc = (y_pred == y).mean()
        print(f"\nEval set accuracy: {acc:.2%}")

        if label_encoder is not None and len(df_eval):
            top10 = df_eval["Disease"].value_counts().head(10).index.tolist()
            mask = df_eval["Disease"].isin(top10)
            if mask.sum():
                idx = np.where(mask.values)[0]
                y_sub = y[idx]
                pred_sub = y_pred[idx]
                labels = [label_encoder.transform([d])[0] for d in top10 if d in known]
                top10_present = [d for d in top10 if d in known]
                if labels:
                    cm = confusion_matrix(y_sub, pred_sub, labels=labels)
                    print("\nConfusion matrix (top diseases by frequency):")
                    print("labels:", top10_present)
                    print(cm)

    sample = pd.DataFrame(
        [
            {
                "Fever": "Yes",
                "Cough": "Yes",
                "Fatigue": "Yes",
                "Difficulty Breathing": "No",
                "Age": 30,
                "Gender": "Female",
                "Blood Pressure": "Normal",
                "Cholesterol Level": "Normal",
            }
        ]
    )
    Xs = prep.transform(sample)
    proba = model.predict_proba(Xs)[0]
    if label_encoder is not None:
        class_names = label_encoder.inverse_transform(model.classes_)
    else:
        class_names = model.classes_
    top3 = proba.argsort()[::-1][:3]
    print("\nSample top-3 predictions:")
    for i in top3:
        print(f"  {class_names[i]}: {proba[i]:.2%}")


if __name__ == "__main__":
    main()
