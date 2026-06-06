#!/usr/bin/env python3
"""Train symptom → disease classifier and export joblib artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    top_k_accuracy_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from device import gpu_device_name, resolve_use_gpu

DEFAULT_DATA = ROOT / "data" / "symptoms" / "Disease_symptom_and_patient_profile_dataset.csv"
DEFAULT_WIDE_DATA = ROOT / "data" / "symptoms" / "kaushil268" / "Training.csv"
DEFAULT_OUT = ROOT.parent / "services" / "api" / "models" / "artifacts"

FEATURE_COLS = [
    "Fever",
    "Cough",
    "Fatigue",
    "Difficulty Breathing",
    "Age",
    "Gender",
    "Blood Pressure",
    "Cholesterol Level",
]
TARGET = "Disease"
WIDE_TARGET = "prognosis"

# Legacy UI fields -> wide symptom column names (kaushil268 / itachi9604)
LEGACY_SYMPTOM_MAP = {
    "fever": ["high_fever", "mild_fever"],
    "cough": ["cough"],
    "fatigue": ["fatigue"],
    "difficulty_breathing": ["breathlessness"],
}

MIN_MACRO_F1 = 0.05
MIN_TOP3_ACC = 0.25
MIN_CLASS_SAMPLES = 2


def filter_rare_classes(df: pd.DataFrame) -> pd.DataFrame:
    counts = df[TARGET].value_counts()
    keep = counts[counts >= MIN_CLASS_SAMPLES].index
    dropped = len(counts) - len(keep)
    if dropped:
        print(f"Excluding {dropped} disease classes with <{MIN_CLASS_SAMPLES} training rows")
    return df[df[TARGET].isin(keep)].copy()


def build_wide_preprocessor(feature_cols: list[str]) -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[("symptoms", "passthrough", feature_cols)],
    )


def load_wide_frame(path: Path) -> tuple[pd.DataFrame, list[str], str]:
    df = pd.read_csv(path)
    drop = [c for c in df.columns if str(c).startswith("Unnamed")]
    df = df.drop(columns=drop, errors="ignore")
    target = WIDE_TARGET if WIDE_TARGET in df.columns else TARGET
    feature_cols = [c for c in df.columns if c != target]
    df = df[feature_cols + [target]].copy()
    for col in feature_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    df[target] = df[target].astype(str).str.strip()
    return df, feature_cols, target


def build_preprocessor() -> ColumnTransformer:
    categorical = [
        "Fever",
        "Cough",
        "Fatigue",
        "Difficulty Breathing",
        "Gender",
        "Blood Pressure",
        "Cholesterol Level",
    ]
    numeric = ["Age"]
    return ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
            ("num", StandardScaler(), numeric),
        ]
    )


def build_xgb(use_gpu: bool) -> tuple[object, str]:
    from xgboost import XGBClassifier

    params = dict(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.08,
        min_child_weight=3,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        eval_metric="mlogloss",
    )
    if use_gpu:
        params["device"] = "cuda"
        params["tree_method"] = "hist"
        version = "xgb-v2.0"
    else:
        params["device"] = "cpu"
        params["tree_method"] = "hist"
        version = "xgb-cpu-v2.0"
    return XGBClassifier(**params), version


def build_rf() -> tuple[RandomForestClassifier, str]:
    return (
        RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            min_samples_leaf=2,
            class_weight="balanced_subsample",
            random_state=42,
            n_jobs=-1,
        ),
        "rf-v2.0",
    )


def build_rf_wide() -> tuple[RandomForestClassifier, str]:
    return (
        RandomForestClassifier(
            n_estimators=300,
            max_depth=18,
            min_samples_leaf=1,
            class_weight="balanced_subsample",
            random_state=42,
            n_jobs=-1,
        ),
        "rf-v3.0-wide",
    )


def cv_scores(
    pipeline: Pipeline,
    X: pd.DataFrame,
    y_enc: np.ndarray,
    *,
    n_splits: int = 5,
) -> dict[str, float]:
    min_class = int(pd.Series(y_enc).value_counts().min())
    n_splits = min(n_splits, min_class, len(np.unique(y_enc)))
    n_splits = max(2, n_splits)
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    y_pred = cross_val_predict(pipeline, X, y_enc, cv=skf, n_jobs=1)
    classes = np.arange(len(np.unique(y_enc)))
    proba = cross_val_predict(pipeline, X, y_enc, cv=skf, method="predict_proba", n_jobs=1)
    return {
        "cv_accuracy": float(accuracy_score(y_enc, y_pred)),
        "cv_macro_f1": float(f1_score(y_enc, y_pred, average="macro", zero_division=0)),
        "cv_top3_accuracy": float(
            top_k_accuracy_score(y_enc, proba, k=min(3, len(classes)), labels=classes)
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--gpu", action="store_true", help="Force NVIDIA GPU (XGBoost CUDA)")
    parser.add_argument("--cpu", action="store_true", help="Force CPU")
    parser.add_argument(
        "--skip-quality-gate",
        action="store_true",
        help="Skip minimum metric checks (dev/synthetic data only)",
    )
    parser.add_argument(
        "--format",
        choices=["legacy", "wide"],
        default="legacy",
        help="legacy=8-field CSV; wide=132 binary symptoms (kaushil268/itachi9604)",
    )
    args = parser.parse_args()

    if args.format == "wide" and args.data == DEFAULT_DATA:
        args.data = DEFAULT_WIDE_DATA

    if args.gpu and args.cpu:
        raise SystemExit("Use only one of --gpu or --cpu")

    gpu_flag = True if args.gpu else False if args.cpu else None
    use_gpu = resolve_use_gpu(gpu_flag)

    if use_gpu:
        print(f"Using GPU: {gpu_device_name() or 'CUDA device 0'}")
    else:
        print("Using CPU")

    if not args.data.exists():
        data_hint = "npm run setup:ml:data"
        if args.format == "wide":
            data_hint = "ml/scripts/prepare_symptoms.py or kaushil268/Training.csv"
        raise SystemExit(f"Dataset not found: {args.data}. Run: {data_hint}")

    wide_mode = args.format == "wide"
    raw_target_col = TARGET
    if wide_mode:
        df_raw, feature_cols, target_col = load_wide_frame(args.data)
        raw_target_col = target_col
        df = filter_rare_classes(df_raw.rename(columns={target_col: TARGET}))
        X = df[feature_cols]
        y_str = df[TARGET]
        preprocessor = build_wide_preprocessor(feature_cols)
        rf_clf, rf_ver = build_rf_wide()
        model_version_prefix = "wide"
    else:
        df_raw = pd.read_csv(args.data)
        df = filter_rare_classes(df_raw)
        X = df[FEATURE_COLS]
        y_str = df[TARGET]
        feature_cols = FEATURE_COLS
        preprocessor = build_preprocessor()
        rf_clf, rf_ver = build_rf()
        model_version_prefix = "legacy"

    label_encoder = LabelEncoder()
    y_enc = label_encoder.fit_transform(y_str)

    n_classes = len(label_encoder.classes_)
    n_samples = len(df)
    print(f"Training ({args.format}) on {n_samples} rows, {n_classes} disease classes (from {len(df_raw)} total rows)")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )

    candidates: list[tuple[str, Pipeline, str, dict]] = []

    if not wide_mode:
        xgb_clf, xgb_ver = build_xgb(use_gpu)
        xgb_pipe = Pipeline([("prep", build_preprocessor()), ("clf", xgb_clf)])
        xgb_cv = cv_scores(xgb_pipe, X, y_enc)
        print(f"XGBoost CV: acc={xgb_cv['cv_accuracy']:.2%} macro_f1={xgb_cv['cv_macro_f1']:.3f} top3={xgb_cv['cv_top3_accuracy']:.2%}")
        candidates.append(("xgb", xgb_pipe, xgb_ver, xgb_cv))

    rf_pipe = Pipeline([("prep", preprocessor), ("clf", rf_clf)])
    rf_cv = cv_scores(rf_pipe, X, y_enc)
    print(f"RandomForest CV: acc={rf_cv['cv_accuracy']:.2%} macro_f1={rf_cv['cv_macro_f1']:.3f} top3={rf_cv['cv_top3_accuracy']:.2%}")
    candidates.append(("rf", rf_pipe, rf_ver, rf_cv))

    scored = sorted(candidates, key=lambda c: c[3]["cv_macro_f1"], reverse=True)
    best_name, best_pipe, model_version, best_cv = scored[0][0], scored[0][1], scored[0][2], scored[0][3]
    print(f"Selected model: {best_name} ({model_version})")

    best_pipe.fit(X_train, y_train)
    X_test_t = best_pipe.named_steps["prep"].transform(X_test)
    clf_fitted = best_pipe.named_steps["clf"]
    y_pred = clf_fitted.predict(X_test_t)
    proba = clf_fitted.predict_proba(X_test_t)
    classes = np.arange(n_classes)

    test_accuracy = float(accuracy_score(y_test, y_pred))
    test_macro_f1 = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
    test_top3 = float(
        top_k_accuracy_score(
            y_test, proba, k=min(3, n_classes), labels=classes
        )
    )

    print(f"Held-out test accuracy: {test_accuracy:.2%}")
    print(f"Held-out macro F1: {test_macro_f1:.3f}")
    print(f"Held-out top-3 accuracy: {test_top3:.2%}")

    if not args.skip_quality_gate:
        if best_cv["cv_macro_f1"] < MIN_MACRO_F1 or best_cv["cv_top3_accuracy"] < MIN_TOP3_ACC:
            raise SystemExit(
                f"Quality gate failed: cv_macro_f1={best_cv['cv_macro_f1']:.3f} "
                f"(min {MIN_MACRO_F1}), cv_top3={best_cv['cv_top3_accuracy']:.2%} "
                f"(min {MIN_TOP3_ACC:.0%}). Use --skip-quality-gate for synthetic data."
            )

    if use_gpu and hasattr(clf_fitted, "set_params"):
        clf_fitted.set_params(device="cpu")

    class_support = (
        pd.Series(y_str).value_counts().sort_index().astype(int).to_dict()
    )
    report = classification_report(
        y_test,
        y_pred,
        labels=np.arange(n_classes),
        target_names=list(label_encoder.classes_),
        output_dict=True,
        zero_division=0,
    )

    metrics = {
        "model_version": model_version,
        "model_type": best_name,
        "feature_format": args.format,
        "n_features": len(feature_cols),
        "n_samples": n_samples,
        "n_samples_raw": len(df_raw),
        "n_classes": n_classes,
        "n_classes_raw": int(df_raw[raw_target_col].nunique()),
        "cv_accuracy": best_cv["cv_accuracy"],
        "cv_macro_f1": best_cv["cv_macro_f1"],
        "cv_top3_accuracy": best_cv["cv_top3_accuracy"],
        "test_accuracy": test_accuracy,
        "test_macro_f1": test_macro_f1,
        "test_top3_accuracy": test_top3,
        "class_support": class_support,
        "classification_report": report,
    }

    args.out.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf_fitted, args.out / "symptom_model.joblib")
    joblib.dump(best_pipe.named_steps["prep"], args.out / "symptom_preprocessor.joblib")
    joblib.dump(label_encoder, args.out / "symptom_label_encoder.joblib")
    classes_list = sorted(df_raw[raw_target_col].unique().tolist())
    (args.out / "disease_classes.json").write_text(json.dumps(classes_list, indent=2))
    (args.out / "model_version.txt").write_text(model_version)
    (args.out / "metrics.json").write_text(json.dumps(metrics, indent=2))
    if wide_mode:
        (args.out / "symptom_features.json").write_text(json.dumps(feature_cols, indent=2))
        (args.out / "legacy_symptom_map.json").write_text(
            json.dumps(LEGACY_SYMPTOM_MAP, indent=2)
        )

    print(f"Model: {model_version}")
    print(f"Artifacts saved to {args.out}")


if __name__ == "__main__":
    main()
