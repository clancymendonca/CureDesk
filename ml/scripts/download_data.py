#!/usr/bin/env python3
"""Legacy wrapper: uom190346a symptoms + BD prescription images."""

from __future__ import annotations

import argparse
import csv
import os
import random
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "ml" / "data"
SCRIPTS_DIR = Path(__file__).resolve().parent
SYMPTOM_CSV = DATA / "symptoms" / "Disease_symptom_and_patient_profile_dataset.csv"


def kaggle_configured() -> bool:
    if os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY"):
        return True
    return (Path.home() / ".kaggle" / "kaggle.json").exists()


def generate_sample_symptoms() -> None:
    dest = DATA / "symptoms"
    dest.mkdir(parents=True, exist_ok=True)
    diseases = ["Influenza", "Common Cold", "Asthma", "Eczema", "Diabetes", "Hypertension"]
    rows = []
    random.seed(42)
    for _ in range(600):
        disease = random.choice(diseases)
        rows.append({
            "Disease": disease,
            "Fever": random.choice(["Yes", "No"]),
            "Cough": random.choice(["Yes", "No"]),
            "Fatigue": random.choice(["Yes", "No"]),
            "Difficulty Breathing": random.choice(["Yes", "No"]),
            "Age": random.randint(5, 85),
            "Gender": random.choice(["Male", "Female"]),
            "Blood Pressure": random.choice(["Normal", "High", "Low"]),
            "Cholesterol Level": random.choice(["Normal", "High"]),
            "Outcome Variable": random.choice(["Positive", "Negative"]),
        })
    with SYMPTOM_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"Sample dataset written to {SYMPTOM_CSV}")


def _run_download_all(*args: str) -> int:
    cmd = [sys.executable, str(SCRIPTS_DIR / "download_all.py"), *args]
    return subprocess.call(cmd)


def download_symptoms(*, allow_synthetic: bool, skip_kaggle_check: bool) -> int:
    if allow_synthetic:
        generate_sample_symptoms()
        return 0

    if not skip_kaggle_check and not kaggle_configured():
        print("ERROR: Kaggle credentials not found.", file=sys.stderr)
        return 1

    rc = _run_download_all("--id", "symptoms_uom190346a")
    if rc != 0:
        return rc

    if not SYMPTOM_CSV.exists():
        print(f"ERROR: Expected {SYMPTOM_CSV} after download", file=sys.stderr)
        return 1

    import pandas as pd

    df = pd.read_csv(SYMPTOM_CSV)
    n_diseases = df["Disease"].nunique()
    if len(df) < 300:
        print(
            f"Symptom dataset too small ({len(df)} rows). "
            "Check Kaggle download or use --allow-synthetic for dev only.",
            file=sys.stderr,
        )
        return 1
    print(f"Symptoms dataset ready: {len(df)} rows, {n_diseases} diseases")
    return 0


def download_prescriptions(*, skip_kaggle_check: bool) -> int:
    if not skip_kaggle_check and not kaggle_configured():
        print("ERROR: Kaggle credentials not found.", file=sys.stderr)
        return 1
    return _run_download_all("--id", "prescriptions_bd")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download legacy CureDesk ML datasets")
    parser.add_argument(
        "--dataset", choices=["symptoms", "prescriptions", "all"], default="all"
    )
    parser.add_argument("--allow-synthetic", action="store_true")
    parser.add_argument("--skip-kaggle-check", action="store_true")
    args = parser.parse_args()

    if args.dataset in ("symptoms", "all"):
        rc = download_symptoms(
            allow_synthetic=args.allow_synthetic,
            skip_kaggle_check=args.skip_kaggle_check,
        )
        if rc != 0:
            raise SystemExit(rc)

    if args.dataset in ("prescriptions", "all"):
        rc = download_prescriptions(skip_kaggle_check=args.skip_kaggle_check)
        if rc != 0:
            raise SystemExit(rc)


if __name__ == "__main__":
    main()
