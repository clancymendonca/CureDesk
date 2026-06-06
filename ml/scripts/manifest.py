"""Read/write ml/data/manifest.json for dataset downloads."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "ml" / "data"
MANIFEST_PATH = DATA_ROOT / "manifest.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.exists():
        return {"version": 1, "datasets": {}}
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def save_manifest(manifest: dict[str, Any]) -> None:
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def get_entry(manifest: dict[str, Any], dataset_id: str) -> dict[str, Any] | None:
    return manifest.get("datasets", {}).get(dataset_id)


def is_complete(manifest: dict[str, Any], dataset_id: str, dest: Path) -> bool:
    if not dest.exists() or not any(dest.rglob("*")):
        return False
    entry = get_entry(manifest, dataset_id)
    if entry and entry.get("status") == "failed":
        return False
    return True


def record_success(
    manifest: dict[str, Any],
    dataset_id: str,
    *,
    dest: Path,
    file_count: int,
    bytes_total: int,
    notes: str = "",
) -> None:
    manifest.setdefault("datasets", {})[dataset_id] = {
        "status": "ok",
        "path": str(dest.relative_to(ROOT)).replace("\\", "/"),
        "file_count": file_count,
        "bytes": bytes_total,
        "downloaded_at": _utc_now(),
        "notes": notes,
    }


def record_failure(manifest: dict[str, Any], dataset_id: str, error: str) -> None:
    manifest.setdefault("datasets", {})[dataset_id] = {
        "status": "failed",
        "error": error,
        "updated_at": _utc_now(),
    }


def record_skipped(manifest: dict[str, Any], dataset_id: str, reason: str) -> None:
    manifest.setdefault("datasets", {})[dataset_id] = {
        "status": "skipped",
        "reason": reason,
        "updated_at": _utc_now(),
    }


def dir_stats(path: Path) -> tuple[int, int]:
    if not path.exists():
        return 0, 0
    count = 0
    total = 0
    for p in path.rglob("*"):
        if p.is_file():
            count += 1
            try:
                total += p.stat().st_size
            except OSError:
                pass
    return count, total
