"""Download NLM RxNorm / RxTerms zip archives."""

from __future__ import annotations

import re
import zipfile
from io import BytesIO
from pathlib import Path

import requests

RXNORM_FILES_PAGE = "https://www.nlm.nih.gov/research/umls/rxnorm/docs/rxnormfiles.html"
RXTERMS_PAGE = "https://lhncbc.nlm.nih.gov/MOR/RxTerms/"
DEFAULT_HEADERS = {
    "User-Agent": "CureDesk-ML-Downloader/1.0 (+https://github.com/curedesk)",
}


def _resolve_rxnorm_url(url: str) -> str:
    """Resolve prescribe/current URLs from the NLM files page when generic links break."""
    if "prescribe_current" not in url and "RxTerms_current" not in url:
        return url

    page = requests.get(RXNORM_FILES_PAGE, headers=DEFAULT_HEADERS, timeout=60)
    page.raise_for_status()
    html = page.text

    if "prescribe_current" in url:
        matches = re.findall(
            r"https://download\.nlm\.nih\.gov/rxnorm/RxNorm_full_prescribe_[0-9]+\.zip",
            html,
        )
        if matches:
            return matches[0]

    if "RxTerms_current" in url or "rxterms" in url.lower():
        page2 = requests.get(RXTERMS_PAGE, headers=DEFAULT_HEADERS, timeout=60)
        page2.raise_for_status()
        rxterms = re.findall(
            r"https://data\.lhncbc\.nlm\.nih\.gov/public/rxterms/release/RxTerms[0-9]+\.zip",
            page2.text,
        )
        if rxterms:
            return rxterms[0]
        rxterms = re.findall(r"https://[^\"'\s<>]+RxTerms[^\"'\s<>]+\.zip", page2.text)
        if rxterms:
            return rxterms[0]

    return url.replace("/umls/kss/rxnorm/", "/rxnorm/")


def download_nlm_zip(url: str, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    resolved = _resolve_rxnorm_url(url)
    resp = requests.get(resolved, headers=DEFAULT_HEADERS, timeout=600)
    resp.raise_for_status()
    data = resp.content
    if not data.startswith(b"PK"):
        raise RuntimeError(
            f"Expected zip archive from {resolved}, got {resp.headers.get('content-type')}"
        )
    zip_path = dest / resolved.split("/")[-1]
    zip_path.write_bytes(data)
    with zipfile.ZipFile(BytesIO(data)) as zf:
        zf.extractall(dest)

