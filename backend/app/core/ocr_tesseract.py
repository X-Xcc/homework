from __future__ import annotations

import logging
import os
from pathlib import Path

import pytesseract
from PIL import Image

from app.config import settings
from app.core.ocr_base import OcrEngine
from app.core.ocr_types import OcrDependencyError, OcrExecutionError, OcrResult

logger = logging.getLogger(__name__)


class TesseractOcrEngine(OcrEngine):
    engine_name = "tesseract"

    def __init__(self) -> None:
        self._configured = False
        self._configure_tesseract()

    def _configure_tesseract(self) -> None:
        configured_cmd = settings.TESSERACT_CMD.strip()
        candidate_paths = [
            configured_cmd,
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]

        for candidate in candidate_paths:
            if candidate and Path(candidate).exists():
                pytesseract.pytesseract.tesseract_cmd = candidate
                self._configured = True
                return

        if configured_cmd:
            pytesseract.pytesseract.tesseract_cmd = configured_cmd
            self._configured = True
            return

        self._configured = True

    def is_available(self) -> bool:
        if not self._configured:
            return False

        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    def extract_text(self, image: Image.Image) -> OcrResult:
        if not self.is_available():
            raise OcrDependencyError(
                "当前环境未安装 Tesseract OCR 或未加入 PATH，请安装 Tesseract 并确认命令可执行。"
            )

        try:
            text = pytesseract.image_to_string(
                image,
                lang=settings.TESSERACT_LANG,
                config=settings.TESSERACT_CONFIG,
            )
            return OcrResult(
                text=text.strip(),
                engine=self.engine_name,
                metadata={
                    "lang": settings.TESSERACT_LANG,
                    "config": settings.TESSERACT_CONFIG,
                },
            )
        except pytesseract.TesseractNotFoundError as exc:
            raise OcrDependencyError(
                "当前环境未安装 Tesseract OCR 或未加入 PATH，请安装 Tesseract 并确认命令可执行。"
            ) from exc
        except Exception as exc:
            logger.exception("Tesseract OCR execution failed")
            raise OcrExecutionError(str(exc)) from exc
