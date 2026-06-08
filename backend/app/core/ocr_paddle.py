from __future__ import annotations

import logging
from typing import Any

import numpy as np
from PIL import Image

from app.config import settings
from app.core.ocr_base import OcrEngine
from app.core.ocr_types import OcrDependencyError, OcrExecutionError, OcrInitializationError, OcrResult

logger = logging.getLogger(__name__)

try:
    from paddleocr import PaddleOCR
except Exception:
    PaddleOCR = None


class PaddleOcrEngine(OcrEngine):
    engine_name = "paddle"

    def __init__(self) -> None:
        self._client: Any | None = None
        self._init_error: Exception | None = None

    def is_available(self) -> bool:
        return PaddleOCR is not None

    def _get_client(self) -> Any:
        if PaddleOCR is None:
            raise OcrDependencyError("PaddleOCR 未安装，请安装 paddleocr 与 paddlepaddle 运行时。")

        if self._client is not None:
            return self._client

        if self._init_error is not None:
            raise OcrInitializationError(str(self._init_error)) from self._init_error

        try:
            self._client = PaddleOCR(
                use_angle_cls=settings.OCR_PADDLE_USE_ANGLE_CLS,
                lang=settings.OCR_LANG,
                use_gpu=settings.OCR_ENABLE_GPU,
                det_limit_side_len=settings.OCR_PADDLE_DET_LIMIT_SIDE_LEN,
                show_log=settings.OCR_PADDLE_SHOW_LOG,
            )
            return self._client
        except Exception as exc:
            self._init_error = exc
            logger.exception("PaddleOCR initialization failed")
            raise OcrInitializationError(str(exc)) from exc

    def extract_text(self, image: Image.Image) -> OcrResult:
        client = self._get_client()

        try:
            image_array = np.array(image.convert("RGB"))
            result = client.ocr(image_array, cls=settings.OCR_PADDLE_USE_ANGLE_CLS)
            lines: list[str] = []
            scores: list[float] = []

            for block in result or []:
                for item in block or []:
                    if len(item) < 2:
                        continue
                    text_info = item[1]
                    if not text_info:
                        continue
                    text = text_info[0]
                    score = float(text_info[1]) if len(text_info) > 1 else None
                    if text:
                        lines.append(text)
                    if score is not None:
                        scores.append(score)

            joined_text = "\n".join(lines).strip()
            avg_score = sum(scores) / len(scores) if scores else None
            return OcrResult(
                text=joined_text,
                engine=self.engine_name,
                score=avg_score,
                metadata={
                    "line_count": len(lines),
                    "avg_confidence": avg_score,
                    "use_gpu": settings.OCR_ENABLE_GPU,
                    "lang": settings.OCR_LANG,
                    "det_limit_side_len": settings.OCR_PADDLE_DET_LIMIT_SIDE_LEN,
                },
            )
        except OcrDependencyError:
            raise
        except OcrInitializationError:
            raise
        except Exception as exc:
            logger.exception("PaddleOCR execution failed")
            raise OcrExecutionError(str(exc)) from exc
