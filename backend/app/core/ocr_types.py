from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class OcrResult:
    text: str
    engine: str
    score: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class OcrEngineError(RuntimeError):
    """Base OCR engine failure."""


class OcrDependencyError(OcrEngineError):
    """OCR engine dependency is unavailable."""


class OcrInitializationError(OcrEngineError):
    """OCR engine failed during initialization."""


class OcrExecutionError(OcrEngineError):
    """OCR engine failed while recognizing an image."""


class OcrQualityError(OcrEngineError):
    """OCR result quality is below the acceptance threshold."""
