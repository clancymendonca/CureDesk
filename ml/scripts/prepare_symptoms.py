"""Prepare itachi9604 / kaushil268 symptom CSVs for wide-format training."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ITACHI_DIR = ROOT / "data" / "symptoms" / "itachi9604"
KAUSHIL_TRAIN = ROOT / "data" / "symptoms" / "kaushil268" / "Training.csv"
OUT_ITACHI = ROOT / "data" / "symptoms" / "itachi9604_binarized.csv"
OUT_KAUSHIL = ROOT / "data" / "symptoms" / "kaushil268_prepared.csv"


def _symptom_vocab(severity_path: Path) -> list[str]:
    df = pd.read_csv(severity_path)
    return df["Symptom"].astype(str).str.strip().tolist()


def binarize_itachi9604() -> Path:
    vocab = _symptom_vocab(ITACHI_DIR / "Symptom-severity.csv")
    vocab_set = set(vocab)
    rows = pd.read_csv(ITACHI_DIR / "dataset.csv")
    symptom_cols = [c for c in rows.columns if c.startswith("Symptom_")]
    records: list[dict[str, int | str]] = []
    for _, row in rows.iterrows():
        disease = str(row["Disease"]).strip()
        active = {
            str(row[c]).strip()
            for c in symptom_cols
            if pd.notna(row[c]) and str(row[c]).strip()
        }
        rec: dict[str, int | str] = {"prognosis": disease}
        for sym in vocab:
            key = sym.replace(" ", "_")
            rec[key] = 1 if sym in active or key in active else 0
        records.append(rec)
    out = pd.DataFrame(records)
    out.to_csv(OUT_ITACHI, index=False)
    print(f"Wrote {len(out)} rows x {len(vocab)} symptoms -> {OUT_ITACHI}")
    return OUT_ITACHI


def prepare_kaushil268() -> Path:
    df = pd.read_csv(KAUSHIL_TRAIN)
    drop = [c for c in df.columns if c.startswith("Unnamed")]
    df = df.drop(columns=drop, errors="ignore")
    df = df.rename(columns={"prognosis": "prognosis"})
    df.to_csv(OUT_KAUSHIL, index=False)
    print(f"Wrote {len(df)} rows -> {OUT_KAUSHIL}")
    return OUT_KAUSHIL


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["itachi9604", "kaushil268", "all"], default="all")
    args = parser.parse_args()
    if args.dataset in ("itachi9604", "all"):
        binarize_itachi9604()
    if args.dataset in ("kaushil268", "all"):
        prepare_kaushil268()


if __name__ == "__main__":
    main()
