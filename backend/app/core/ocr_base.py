from __future__ import annotations

from abc import ABC, abstractmethod
from PIL import Image

from app.core.ocr_types import OcrResult


class OcrEngine(ABC):
    engine_name: str

    @abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def extract_text(self, image: Image.Image) -> OcrResult:
        raise NotImplementedError
