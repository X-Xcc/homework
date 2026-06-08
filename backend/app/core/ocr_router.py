from __future__ import annotations

import logging
import time
from typing import Iterable

from PIL import Image

from app.config import settings
from app.core.ocr_base import OcrEngine
from app.core.ocr_quality import OcrQualityChecker
from app.core.ocr_types import OcrEngineError, OcrQualityError, OcrResult

logger = logging.getLogger(__name__)


class OcrEngineRouter(OcrEngine):
    engine_name = "router"

    def __init__(self, primary_engine: OcrEngine, fallback_engines: Iterable[OcrEngine] | None = None):
        self.primary_engine = primary_engine
        self.fallback_engines = list(fallback_engines or [])
        self.quality_checker = OcrQualityChecker()

    def is_available(self) -> bool:
        return self.primary_engine.is_available() or any(engine.is_available() for engine in self.fallback_engines)

    def extract_text(self, image: Image.Image) -> OcrResult:
        last_error: Exception | None = None
        engines = [self.primary_engine, *self.fallback_engines]

        for index, engine in enumerate(engines):
            started = time.perf_counter()
            try:
                result = engine.extract_text(image)
                assessment = self.quality_checker.assess(result.text)
                elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
                result.metadata.update(
                    {
                        "quality_score": assessment.score,
                        "quality_reasons": assessment.reasons,
                        "elapsed_ms": elapsed_ms,
                        "fallback_used": index > 0,
                    }
                )

                if not assessment.passed:
                    raise OcrQualityError(
                        f"engine={engine.engine_name}, score={assessment.score:.2f}, reasons={','.join(assessment.reasons)}"
                    )

                return result
            except OcrEngineError as exc:
                elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
                logger.warning(
                    "OCR engine failed, trying next engine if available",
                    extra={
                        "engine": engine.engine_name,
                        "elapsed_ms": elapsed_ms,
                        "error": str(exc),
                    },
                )
                last_error = exc
                continue

        raise OcrEngineError(str(last_error) if last_error else "没有可用的 OCR 引擎")


def build_ocr_engine(paddle_engine: OcrEngine, tesseract_engine: OcrEngine) -> OcrEngineRouter:
    registry = {
        "paddle": paddle_engine,
        "tesseract": tesseract_engine,
    }

    primary_name = settings.OCR_PRIMARY_ENGINE
    fallback_name = settings.OCR_FALLBACK_ENGINE

    primary = registry.get(primary_name, paddle_engine)
    fallback = registry.get(fallback_name, tesseract_engine)

    fallback_engines: list[OcrEngine] = []
    if fallback is not primary:
        fallback_engines.append(fallback)

    return OcrEngineRouter(primary_engine=primary, fallback_engines=fallback_engines)
