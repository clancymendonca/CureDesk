"""Shared OCR preprocessing, extraction, and drug matching."""

from __future__ import annotations

from typing import Optional

import cv2
import numpy as np
from rapidfuzz import fuzz, process


def decode_grayscale(image_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Invalid image")
    return img


def _resize(img: np.ndarray, max_dim: int = 1200) -> np.ndarray:
    h, w = img.shape[:2]
    if max(h, w) <= max_dim:
        return img
    scale = max_dim / max(h, w)
    return cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)


def _variant_adaptive(img: np.ndarray) -> np.ndarray:
    return cv2.adaptiveThreshold(
        img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )


def _variant_clahe_otsu(img: np.ndarray) -> np.ndarray:
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(img)
    denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
    _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


def _variant_adaptive_mean(img: np.ndarray) -> np.ndarray:
    denoised = cv2.bilateralFilter(img, 9, 75, 75)
    return cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 10
    )


def preprocess_variants(image_bytes: bytes) -> list[np.ndarray]:
    gray = _resize(decode_grayscale(image_bytes))
    return [
        gray,
        _variant_adaptive(gray),
        _variant_clahe_otsu(gray),
        _variant_adaptive_mean(gray),
    ]


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """Default single variant (backward compatible)."""
    gray = decode_grayscale(image_bytes)
    return _variant_adaptive(_resize(gray))


def _easyocr_read(reader, img: np.ndarray) -> tuple[str, float]:
    results = reader.readtext(img, detail=1)
    if not results:
        return "", 0.0
    texts = []
    confidences = []
    for item in results:
        if len(item) >= 3:
            texts.append(str(item[1]))
            confidences.append(float(item[2]))
    text = " ".join(texts).strip()
    score = sum(confidences) / len(confidences) if confidences else 0.0
    return text, score


def _paddle_read(reader, img: np.ndarray) -> tuple[str, float]:
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    result = reader.ocr(img, cls=True)
    if not result or not result[0]:
        return "", 0.0
    texts = []
    confidences = []
    for line in result[0]:
        if line and len(line) >= 2:
            texts.append(line[1][0])
            confidences.append(float(line[1][1]))
    text = " ".join(texts).strip()
    score = sum(confidences) / len(confidences) if confidences else 0.0
    return text, score


def extract_text_with_engine(
    image_bytes: bytes,
    *,
    engine: str = "easyocr",
    use_gpu: bool = False,
    easyocr_reader=None,
    paddle_reader=None,
) -> str:
    variants = preprocess_variants(image_bytes)
    best_text = ""
    best_score = -1.0

    if engine in ("easyocr", "ensemble"):
        if easyocr_reader is None:
            import easyocr

            easyocr_reader = easyocr.Reader(["en"], gpu=use_gpu)
        for img in variants:
            text, score = _easyocr_read(easyocr_reader, img)
            if score > best_score and text:
                best_score = score
                best_text = text

    if engine in ("paddle", "ensemble"):
        try:
            if paddle_reader is None:
                from paddleocr import PaddleOCR

                paddle_reader = PaddleOCR(
                    use_angle_cls=True,
                    lang="en",
                    use_gpu=use_gpu,
                    show_log=False,
                )
            for img in variants:
                text, score = _paddle_read(paddle_reader, img)
                if score > best_score and text:
                    best_score = score
                    best_text = text
        except ImportError:
            if engine == "paddle":
                raise

    if engine == "ensemble" and easyocr_reader is not None:
        parts: set[str] = set()
        for img in variants[:2]:
            t, _ = _easyocr_read(easyocr_reader, img)
            parts.update(t.lower().split())
        if paddle_reader is not None:
            for img in variants[:2]:
                t, _ = _paddle_read(paddle_reader, img)
                parts.update(t.lower().split())
        if parts:
            merged = " ".join(sorted(parts))
            if len(merged) > len(best_text):
                best_text = merged

    return best_text.strip()


def _drug_choices(drug_list: list[tuple[str, str]]) -> dict[str, tuple[str, str]]:
    choices: dict[str, tuple[str, str]] = {}
    for brand, generic in drug_list:
        choices[brand.lower()] = (brand, generic)
        choices[generic.lower()] = (brand, generic)
        for part in brand.lower().split():
            if len(part) >= 3:
                choices.setdefault(part, (brand, generic))
    return choices


def match_drugs(
    ocr_text: str,
    drug_list: list[tuple[str, str]],
    limit: int = 5,
    min_score: float = 60.0,
) -> list[dict]:
    choices = _drug_choices(drug_list)
    if not choices:
        return []

    matches: dict[str, dict] = {}
    lower = ocr_text.lower()
    tokens = lower.split()

    for token in tokens:
        if len(token) < 3:
            continue
        result = process.extractOne(token, choices.keys(), scorer=fuzz.ratio)
        if result and result[1] >= min_score:
            brand, generic = choices[result[0]]
            key = brand.lower()
            conf = result[1] / 100.0
            if key not in matches or matches[key]["confidence"] < conf:
                matches[key] = {"brand": brand, "generic": generic, "confidence": conf}

    for n in (2, 3):
        for i in range(len(tokens) - n + 1):
            phrase = " ".join(tokens[i : i + n])
            if len(phrase) < 4:
                continue
            result = process.extractOne(phrase, choices.keys(), scorer=fuzz.token_set_ratio)
            if result and result[1] >= min_score:
                brand, generic = choices[result[0]]
                key = brand.lower()
                conf = result[1] / 100.0
                if key not in matches or matches[key]["confidence"] < conf:
                    matches[key] = {"brand": brand, "generic": generic, "confidence": conf}

    full = process.extractOne(lower, choices.keys(), scorer=fuzz.partial_ratio)
    if full and full[1] >= max(min_score, 70):
        brand, generic = choices[full[0]]
        key = brand.lower()
        conf = full[1] / 100.0
        if key not in matches or matches[key]["confidence"] < conf:
            matches[key] = {"brand": brand, "generic": generic, "confidence": conf}

    return sorted(matches.values(), key=lambda x: x["confidence"], reverse=True)[:limit]


def lookup_drugs_from_db(
    ocr_text: str,
    drugs: list[tuple[str, str]],
    limit: int = 5,
) -> list[dict]:
    return match_drugs(ocr_text, drugs, limit=limit)
