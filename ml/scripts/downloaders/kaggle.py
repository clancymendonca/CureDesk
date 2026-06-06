"""Download Kaggle datasets via kagglehub."""

from __future__ import annotations

import shutil
from pathlib import Path


def download_kaggle_dataset(slug: str, dest: Path) -> None:
    import kagglehub

    dest.mkdir(parents=True, exist_ok=True)
    cache_path = Path(kagglehub.dataset_download(slug))
    if not cache_path.exists():
        raise FileNotFoundError(f"Kaggle cache missing after download: {cache_path}")

    for src in cache_path.rglob("*"):
        if not src.is_file():
            continue
        rel = src.relative_to(cache_path)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            continue
        shutil.copy2(src, target)
