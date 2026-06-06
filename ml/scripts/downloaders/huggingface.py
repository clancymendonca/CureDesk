"""Download Hugging Face datasets to local CSV/Parquet."""

from __future__ import annotations

from pathlib import Path

from dataset_registry import DatasetEntry


def download_hf_dataset(entry: DatasetEntry, dest: Path, *, include_large: bool = False) -> None:
    from datasets import load_dataset

    dest.mkdir(parents=True, exist_ok=True)

    if entry.id == "symptoms_hf_dhivyeshrk":
        ds = load_dataset(entry.slug, split="dhivyeshrk")
        out = dest / "dhivyeshrk.csv"
        ds.to_csv(str(out))
        return

    if entry.id == "rag_medical_qa_lavita":
        _export_lavita_subset(entry.slug, dest, full=False)
        return

    if entry.id == "rag_medical_qa_lavita_full":
        _export_lavita_subset(entry.slug, dest, full=True)
        return

    if entry.id == "symptoms_hf_consolidated":
        ds_dict = load_dataset(entry.slug)
        for split_name, split_ds in ds_dict.items():
            out = dest / f"{split_name}.csv"
            split_ds.to_csv(str(out))
        return

    ds_dict = load_dataset(entry.slug)
    if hasattr(ds_dict, "items"):
        for split_name, split_ds in ds_dict.items():
            out = dest / f"{split_name}.csv"
            split_ds.to_csv(str(out))
    else:
        out = dest / "data.csv"
        ds_dict.to_csv(str(out))


def _export_lavita_subset(slug: str, dest: Path, *, full: bool) -> None:
    from datasets import load_dataset

    if full:
        ds_dict = load_dataset(slug)
        for split_name, split_ds in ds_dict.items():
            out = dest / f"{split_name}.csv"
            split_ds.to_csv(str(out))
        return

    # Default: smaller health-oriented configs when available
    preferred = [
        "medical_meadow_medqa",
        "medical_meadow_health_advice",
        "medical_meadow_wikidoc",
        "chatdoctor_healthcaremagic",
    ]
    exported = 0
    for config in preferred:
        try:
            ds = load_dataset(slug, config, split="train")
            out = dest / f"{config}.csv"
            ds.to_csv(str(out))
            exported += 1
        except Exception:
            continue

    if exported == 0:
        ds = load_dataset(slug, split="train[:5000]")
        ds.to_csv(str(dest / "train_subset.csv"))
