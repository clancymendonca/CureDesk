"""Download Mendeley Data datasets via datahugger."""

from __future__ import annotations

from pathlib import Path


def download_mendeley_dataset(doi: str, dest: Path) -> None:
    try:
        import datahugger
    except ImportError as e:
        raise ImportError("pip install datahugger") from e

    dest.mkdir(parents=True, exist_ok=True)
    datahugger.get(doi, str(dest))
