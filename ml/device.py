"""CUDA / RTX GPU detection for ML training and OCR."""

from __future__ import annotations


def cuda_available() -> bool:
    try:
        import torch

        return torch.cuda.is_available()
    except ImportError:
        return False


def gpu_device_name() -> str | None:
    try:
        import torch

        if torch.cuda.is_available():
            return torch.cuda.get_device_name(0)
    except ImportError:
        pass
    return None


def resolve_use_gpu(gpu: bool | None = None) -> bool:
    """Resolve GPU flag: None = auto-detect CUDA (RTX etc.)."""
    if gpu is False:
        return False
    if gpu is True:
        if not cuda_available():
            raise SystemExit(
                "GPU requested but CUDA is not available. "
                "Install CUDA-enabled PyTorch (see ml/requirements-gpu.txt) or pass --cpu."
            )
        return True
    return cuda_available()


def resolve_ocr_gpu(gpu: bool | None = None) -> bool:
    """Same as resolve_use_gpu — EasyOCR uses PyTorch CUDA backend."""
    return resolve_use_gpu(gpu) if gpu is not None else cuda_available()
