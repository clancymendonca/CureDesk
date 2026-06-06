#!/usr/bin/env python3
"""Download all recommended CureDesk ML datasets."""

from __future__ import annotations

import argparse
import csv
import shutil
import sys
import zipfile
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parents[1]
DATA_ROOT = ROOT / "ml" / "data"

sys.path.insert(0, str(SCRIPTS_DIR))

from dataset_registry import DatasetEntry, Group, all_datasets, datasets_for_group, get_dataset
from manifest import (
    DATA_ROOT as MANIFEST_DATA_ROOT,
    dir_stats,
    is_complete,
    load_manifest,
    record_failure,
    record_skipped,
    record_success,
    save_manifest,
)
from downloaders.huggingface import download_hf_dataset
from downloaders.kaggle import download_kaggle_dataset
from downloaders.mendeley import download_mendeley_dataset
from downloaders.nlm import download_nlm_zip

assert MANIFEST_DATA_ROOT == DATA_ROOT


def sync_legacy_paths() -> None:
    """Keep backward-compatible paths for existing train/seed/eval scripts."""
    uom_dir = DATA_ROOT / "symptoms" / "uom190346a"
    legacy_symptom = DATA_ROOT / "symptoms" / "Disease_symptom_and_patient_profile_dataset.csv"
    if uom_dir.exists():
        csvs = list(uom_dir.rglob("*.csv"))
        if csvs:
            shutil.copy2(csvs[0], legacy_symptom)

    bd_dir = DATA_ROOT / "prescriptions" / "bd_handwritten"
    images_dest = DATA_ROOT / "prescriptions" / "images"
    if bd_dir.exists():
        images_dest.mkdir(parents=True, exist_ok=True)
        required: set[str] = set()
        labels = DATA_ROOT / "prescriptions" / "validation_labels.csv"
        if labels.exists():
            with labels.open(newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    img = row.get("IMAGE", "").strip()
                    if img:
                        required.add(img)
        for src in bd_dir.rglob("*"):
            if not src.is_file():
                continue
            if src.suffix.lower() in {".png", ".jpg", ".jpeg"}:
                name = src.name
                if src.suffix.lower() == ".jpg":
                    alt = f"{src.stem}.png"
                    if alt in required:
                        name = alt
                target = images_dest / name
                if not target.exists():
                    shutil.copy2(src, target)


def download_entry(entry: DatasetEntry, *, force: bool, include_large: bool) -> bool:
    """Return True on success, False on failure."""
    dest = DATA_ROOT / entry.dest
    manifest = load_manifest()

    if not force and is_complete(manifest, entry.id, dest):
        print(f"[skip] {entry.id} already downloaded -> {dest}")
        return True

    print(f"[download] {entry.id} -> {dest}")
    try:
        if entry.method == "kaggle":
            download_kaggle_dataset(entry.slug, dest)
        elif entry.method == "hf":
            download_hf_dataset(entry, dest, include_large=include_large)
        elif entry.method == "mendeley":
            download_mendeley_dataset(entry.doi, dest)
        elif entry.method == "nlm":
            download_nlm_zip(entry.url, dest)
        else:
            raise ValueError(f"Unknown method: {entry.method}")

        count, size = dir_stats(dest)
        if count == 0:
            raise RuntimeError("Download finished but destination is empty")

        manifest = load_manifest()
        record_success(manifest, entry.id, dest=dest, file_count=count, bytes_total=size)
        save_manifest(manifest)
        print(f"[ok] {entry.id}: {count} files, {size / 1_048_576:.1f} MB")
        return True
    except Exception as e:
        manifest = load_manifest()
        record_failure(manifest, entry.id, str(e))
        save_manifest(manifest)
        print(f"[fail] {entry.id}: {e}", file=sys.stderr)
        if entry.manual_url:
            print(f"       Manual: {entry.manual_url}", file=sys.stderr)
        return False


def run_downloads(
    entries: list[DatasetEntry],
    *,
    force: bool = False,
    include_large: bool = False,
    continue_on_error: bool = True,
) -> list[str]:
    failed: list[str] = []
    for entry in entries:
        ok = download_entry(entry, force=force, include_large=include_large)
        if not ok:
            failed.append(entry.id)
            if not continue_on_error:
                break

    if any(e.id in ("symptoms_uom190346a", "prescriptions_bd") for e in entries):
        sync_legacy_paths()

    return failed


def import_rxhandbd(zips: list[Path]) -> None:
    """Extract manually downloaded RxHandBD zips into ml/data/prescriptions/rxhandbd/."""
    entry = get_dataset("prescriptions_rxhandbd")
    dest = DATA_ROOT / entry.dest
    dest.mkdir(parents=True, exist_ok=True)

    for src in zips:
        if not src.exists():
            raise FileNotFoundError(src)
        if src.suffix == ".crdownload":
            raise RuntimeError(
                f"{src.name} is still downloading — wait for Chrome to finish, "
                "then rename to .zip"
            )
        with zipfile.ZipFile(src) as zf:
            bad = zf.testzip()
            if bad:
                raise RuntimeError(f"Corrupt zip entry in {src}: {bad}")
            zf.extractall(dest)
        print(f"[import] {src.name} -> {dest}")

    count, size = dir_stats(dest)
    if count == 0:
        raise RuntimeError("No files extracted")

    manifest = load_manifest()
    record_success(
        manifest,
        entry.id,
        dest=dest,
        file_count=count,
        bytes_total=size,
        notes="manual import",
    )
    save_manifest(manifest)
    print(f"[ok] {entry.id}: {count} files, {size / 1_048_576:.1f} MB")


def print_summary() -> None:
    manifest = load_manifest()
    datasets = manifest.get("datasets", {})
    ok = sum(1 for v in datasets.values() if v.get("status") == "ok")
    fail = sum(1 for v in datasets.values() if v.get("status") == "failed")
    skip = sum(1 for v in datasets.values() if v.get("status") == "skipped")
    print(
        f"\nManifest: {ok} ok, {skip} skipped, {fail} failed "
        f"({len(datasets)} entries) -> {DATA_ROOT / 'manifest.json'}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Download CureDesk ML datasets")
    parser.add_argument("--all", action="store_true", help="Download all recommended datasets")
    parser.add_argument(
        "--legacy",
        action="store_true",
        help="Download legacy uom190346a + BD prescriptions only",
    )
    parser.add_argument(
        "--group",
        choices=["symptoms", "prescriptions", "drugs", "rag"],
        action="append",
        help="Download a dataset group (repeatable)",
    )
    parser.add_argument("--id", dest="ids", action="append", help="Download specific dataset id")
    parser.add_argument("--include-large", action="store_true", help="Include large datasets")
    parser.add_argument("--force", action="store_true", help="Re-download even if present")
    parser.add_argument(
        "--import-rxhandbd",
        nargs="+",
        metavar="ZIP",
        help="Import manual RxHandBD zip(s) into prescriptions/rxhandbd/",
    )
    args = parser.parse_args()

    if args.import_rxhandbd:
        import_rxhandbd([Path(p) for p in args.import_rxhandbd])
        print_summary()
        return

    if args.legacy:
        entries = [get_dataset("symptoms_uom190346a"), get_dataset("prescriptions_bd")]
    elif args.ids:
        entries = [get_dataset(i) for i in args.ids]
    elif args.group:
        entries = []
        for g in args.group:
            entries.extend(datasets_for_group(g, include_large=args.include_large))
    elif args.all:
        entries = all_datasets(include_large=args.include_large)
    else:
        parser.error("Specify --all, --legacy, --group, or --id")

    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    failed = run_downloads(entries, force=args.force, include_large=args.include_large)
    print_summary()

    required_failed = [
        fid for fid in failed
        if not get_dataset(fid).optional
    ]
    if required_failed:
        print("\nRetry failed datasets:", file=sys.stderr)
        for fid in required_failed:
            print(f"  python ml/scripts/download_all.py --id {fid}", file=sys.stderr)
        raise SystemExit(len(required_failed))
    if failed:
        print(f"\n{len(failed)} optional dataset(s) failed (see manifest).")


if __name__ == "__main__":
    main()
