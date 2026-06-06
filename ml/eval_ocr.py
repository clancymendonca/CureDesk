#!/usr/bin/env python3
"""Evaluate prescription OCR against label CSVs."""

from __future__ import annotations

import argparse
import csv
import sys
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
DEFAULT_LABELS = ROOT / "data" / "prescriptions" / "validation_labels.csv"
DEFAULT_IMAGES = ROOT / "data" / "prescriptions" / "images"
RXHANDBD_LABELS = ROOT / "data" / "prescriptions" / "rxhandbd" / "RxHandBD-ML" / "Test_Label.csv"
RXHANDBD_IMAGES = ROOT / "data" / "prescriptions" / "rxhandbd" / "RxHandBD-ML" / "Test_Set"


def resolve_image(images_dir: Path, name: str, search_roots: list[Path] | None = None) -> Path | None:
    direct = images_dir / name
    if direct.exists():
        return direct
    for root in search_roots or []:
        candidate = root / name
        if candidate.exists():
            return candidate
    return None


def normalize_label_row(row: dict, fmt: str) -> tuple[str, str, str]:
    """Return (image_name, expected_brand, expected_generic_or_text)."""
    if fmt == "rxhandbd":
        return (
            row.get("Images", row.get("IMAGE", "")).strip(),
            row.get("Text", "").strip(),
            row.get("Text", "").strip(),
        )
    return (
        row.get("IMAGE", "").strip(),
        row.get("MEDICINE_NAME", "").strip(),
        row.get("GENERIC_NAME", "").strip(),
    )


def load_drug_list(labels_path: Path) -> list[tuple[str, str]]:
    seen: set[tuple[str, str]] = set()
    drugs: list[tuple[str, str]] = []
    with labels_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            brand = row.get("MEDICINE_NAME", "").strip()
            generic = row.get("GENERIC_NAME", "").strip()
            if brand and (brand, generic) not in seen:
                seen.add((brand, generic))
                drugs.append((brand, generic))
    return drugs


def load_drugs_from_rxterms(limit: int = 8000) -> list[tuple[str, str]]:
    rx_dir = ROOT / "data" / "drugs" / "rxterms"
    txt_files = [p for p in sorted(rx_dir.glob("RxTerms*.txt")) if "Ingredients" not in p.name]
    if not txt_files:
        return []
    seen: set[tuple[str, str]] = set()
    drugs: list[tuple[str, str]] = []
    with txt_files[0].open(encoding="utf-8") as f:
        header = f.readline().strip().split("|")
        idx = {name: i for i, name in enumerate(header)}
        for line in f:
            if len(drugs) >= limit:
                break
            parts = line.strip().split("|")
            if len(parts) < len(header):
                continue
            brand = parts[idx.get("DISPLAY_NAME", 0)].strip() if "DISPLAY_NAME" in idx else ""
            generic = parts[idx.get("FULL_GENERIC_NAME", 0)].strip() if "FULL_GENERIC_NAME" in idx else ""
            psn = parts[idx.get("PSN", 0)].strip() if "PSN" in idx else ""
            if not brand:
                brand = psn or generic
            if not generic:
                generic = psn or brand
            if not brand:
                continue
            key = (brand[:255], generic[:255])
            if key in seen:
                continue
            seen.add(key)
            drugs.append(key)
    return drugs


def char_overlap(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", type=Path, default=DEFAULT_LABELS)
    parser.add_argument("--images", type=Path, default=DEFAULT_IMAGES)
    parser.add_argument("--gpu", action="store_true", help="Force OCR on NVIDIA GPU")
    parser.add_argument("--cpu", action="store_true", help="Force OCR on CPU")
    parser.add_argument("--engine", choices=["easyocr", "paddle", "ensemble"], default="easyocr")
    parser.add_argument("--limit", type=int, default=0, help="Max images (0 = all)")
    parser.add_argument(
        "--labels-format",
        choices=["bd", "rxhandbd"],
        default="bd",
        help="Label CSV format",
    )
    parser.add_argument(
        "--drug-source",
        choices=["labels", "rxterms"],
        default="labels",
        help="Drug list for fuzzy matching (rxterms = 8k prescribable names)",
    )
    args = parser.parse_args()

    if args.labels_format == "rxhandbd" and args.labels == DEFAULT_LABELS:
        args.labels = RXHANDBD_LABELS
    if args.labels_format == "rxhandbd" and args.images == DEFAULT_IMAGES:
        args.images = RXHANDBD_IMAGES

    if not args.labels.exists():
        raise SystemExit(f"Labels not found: {args.labels}")

    from ocr.drug_lookup import match_drugs
    from ocr.pipeline_core import extract_text_with_engine

    drug_list = (
        load_drugs_from_rxterms()
        if args.drug_source == "rxterms"
        else load_drug_list(args.labels)
    )
    print(f"Drug lookup list: {len(drug_list)} entries ({args.drug_source})")

    if not args.images.exists():
        print(f"No image directory at {args.images}")
        print("Run: npm run setup:ml:data")
        print(f"Loaded {len(drug_list)} unique drugs from labels for lookup testing.")
        sample_text = "Aceta Paracetamol 500mg"
        matches = match_drugs(sample_text, drug_list)
        print(f"\nSample lookup on '{sample_text}':")
        for m in matches[:3]:
            print(f"  {m['brand']} -> {m['generic']} ({m['confidence']:.0%})")
        return

    try:
        import easyocr
    except ImportError:
        raise SystemExit("easyocr not installed — pip install easyocr")

    from device import gpu_device_name, resolve_ocr_gpu

    gpu_flag = True if args.gpu else False if args.cpu else None
    use_gpu = resolve_ocr_gpu(gpu_flag)
    print(f"OCR engine: {args.engine}, GPU: {use_gpu} ({gpu_device_name() or 'CPU'})")

    reader = easyocr.Reader(["en"], gpu=use_gpu) if args.engine in ("easyocr", "ensemble") else None
    paddle_reader = None
    if args.engine in ("paddle", "ensemble"):
        try:
            from paddleocr import PaddleOCR

            paddle_reader = PaddleOCR(
                use_angle_cls=True, lang="en", use_gpu=use_gpu, show_log=False
            )
        except ImportError:
            if args.engine == "paddle":
                raise SystemExit("paddleocr not installed")

    brand_ok = generic_ok = 0
    text_ok = 0
    total = 0
    overlaps: list[float] = []

    search_roots = [args.images.parent] if args.labels_format == "rxhandbd" else []
    if args.labels_format == "rxhandbd":
        search_roots.append(args.images.parent.parent / "RxHandBD-ML" / "Train_Set")
        search_roots.append(args.images.parent.parent / "RxHandBD-Raw")

    with args.labels.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if args.limit > 0:
        rows = rows[: args.limit]

    for row in rows:
        image_name, expected_brand, expected_generic = normalize_label_row(row, args.labels_format)
        if not image_name:
            continue
        image_path = resolve_image(args.images, image_name, search_roots)
        if not image_path:
            continue

        total += 1
        img_bytes = image_path.read_bytes()
        ocr_text = extract_text_with_engine(
            img_bytes,
            engine=args.engine,
            use_gpu=use_gpu,
            easyocr_reader=reader,
            paddle_reader=paddle_reader,
        )
        overlap = max(
            char_overlap(ocr_text, expected_brand),
            char_overlap(ocr_text, expected_generic),
        )
        overlaps.append(overlap)
        if overlap >= 0.5:
            text_ok += 1
        if args.labels_format == "bd":
            matches = match_drugs(ocr_text, drug_list)
            if matches and matches[0]["brand"].lower() == expected_brand.lower():
                brand_ok += 1
            if matches and matches[0]["generic"].lower() == expected_generic.lower():
                generic_ok += 1

    if total == 0:
        print(f"Images directory exists but no labeled images found under {args.images}")
        print("Run: npm run setup:ml:data")
    else:
        mean_overlap = sum(overlaps) / len(overlaps)
        print(f"Dataset: {args.labels_format}, evaluated {total} images")
        if args.labels_format == "bd":
            print(f"Brand exact-match rate: {brand_ok}/{total} ({brand_ok / total:.1%})")
            print(f"Generic exact-match rate: {generic_ok}/{total} ({generic_ok / total:.1%})")
        print(f"Text overlap >=50%: {text_ok}/{total} ({text_ok / total:.1%})")
        print(f"Mean OCR char overlap vs label: {mean_overlap:.1%}")


if __name__ == "__main__":
    main()
