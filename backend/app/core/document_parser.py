from __future__ import annotations

import logging
import re
from io import BytesIO
from pathlib import Path
from typing import Optional

import PyPDF2
import pdfplumber
from docx import Document
from PIL import Image, ImageEnhance, ImageOps

from app.config import settings
from app.core.ocr import PaddleOcrEngine, TesseractOcrEngine, build_ocr_engine
from app.core.ocr_base import OcrEngine
from app.core.ocr_quality import OcrQualityAssessment, OcrQualityChecker
from app.core.ocr_types import (
    OcrDependencyError,
    OcrEngineError,
    OcrExecutionError,
    OcrInitializationError,
    OcrQualityError,
    OcrResult,
)

logger = logging.getLogger(__name__)


class DocumentParser:
    def __init__(self, ocr_engine: OcrEngine):
        self.supported_extensions = {".pdf", ".docx", ".txt", ".jpg", ".jpeg", ".png"}
        self.ocr_engine = ocr_engine
        self.quality_checker = OcrQualityChecker()

    def parse(self, file_path: str) -> str:
        ext = Path(file_path).suffix.lower()

        if ext not in self.supported_extensions:
            raise ValueError(f"不支持的文件格式: {ext}")

        if ext == ".pdf":
            return self._parse_pdf(file_path)
        if ext == ".docx":
            return self._parse_docx(file_path)
        if ext == ".txt":
            return self._parse_txt(file_path)
        if ext in {".jpg", ".jpeg", ".png"}:
            return self._parse_image(file_path)
        raise ValueError(f"不支持的文件格式: {ext}")

    def _parse_pdf(self, file_path: str) -> str:
        text = ""

        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

        return text.strip()

    def _parse_docx(self, file_path: str) -> str:
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs if para.text])
        return text.strip()

    def _parse_txt(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    def _parse_image(self, file_path: str) -> str:
        try:
            image = Image.open(file_path)
            image = self._preprocess_image_for_ocr(image)
            result = self.ocr_engine.extract_text(image)
            result.text = self._normalize_ocr_text(result.text)
            assessment = self.quality_checker.assess(result.text)
            self._log_ocr_result(file_path, result, assessment)
            if not assessment.passed:
                raise OcrQualityError(
                    f"OCR识别结果质量不足: engine={result.engine}, score={assessment.score:.2f}, reasons={','.join(assessment.reasons)}"
                )
            return result.text.strip()
        except OcrDependencyError as e:
            raise RuntimeError(f"OCR依赖缺失: {str(e)}") from e
        except OcrInitializationError as e:
            raise RuntimeError(f"OCR初始化失败: {str(e)}") from e
        except OcrQualityError as e:
            raise RuntimeError(str(e)) from e
        except OcrExecutionError as e:
            raise RuntimeError(f"OCR识别失败: {str(e)}") from e
        except OcrEngineError as e:
            raise RuntimeError(f"OCR处理失败: {str(e)}") from e
        except Exception as e:
            raise RuntimeError(f"OCR识别失败: {str(e)}") from e

    def _preprocess_image_for_ocr(self, image: Image.Image) -> Image.Image:
        processed = image.convert("L")

        min_width = settings.OCR_MIN_WIDTH
        if processed.width < min_width:
            scale = min_width / processed.width
            processed = processed.resize(
                (int(processed.width * scale), int(processed.height * scale)),
                Image.Resampling.LANCZOS,
            )

        processed = ImageOps.autocontrast(processed, cutoff=settings.OCR_AUTO_CONTRAST_CUTOFF)
        processed = ImageEnhance.Contrast(processed).enhance(settings.OCR_CONTRAST_FACTOR)
        processed = ImageEnhance.Sharpness(processed).enhance(settings.OCR_SHARPEN_FACTOR)

        threshold = settings.OCR_BINARIZE_THRESHOLD
        if threshold > 0:
            processed = processed.point(lambda pixel: 255 if pixel > threshold else 0)
        return processed

    def _log_ocr_result(self, file_path: str, result: OcrResult, assessment: OcrQualityAssessment) -> None:
        logger.info(
            "OCR parse completed",
            extra={
                "file_path": file_path,
                "ocr_engine": result.engine,
                "ocr_score": result.score,
                "quality_score": assessment.score,
                "quality_reasons": assessment.reasons,
                "ocr_metadata": result.metadata,
            },
        )

    def _normalize_ocr_text(self, text: str) -> str:
        normalized = (text or "").strip()
        if not normalized:
            return normalized

        normalized = re.sub(r"[ \t]+", " ", normalized)
        normalized = re.sub(r" *\n+ *", "\n", normalized)

        if settings.OCR_JOIN_CJK_SPACES:
            normalized = re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])", "", normalized)
            normalized = re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[，。；：！？、“”‘’（）《》])", "", normalized)
            normalized = re.sub(r"(?<=[，。；：！？、“”‘’（）《》])\s+(?=[\u4e00-\u9fff])", "", normalized)

        return normalized.strip()

    def validate_file(self, file_path: str, max_size: int) -> tuple[bool, str]:
        path = Path(file_path)
        if not path.exists():
            return False, "文件不存在"

        ext = path.suffix.lower()
        if ext not in self.supported_extensions:
            return False, f"不支持的文件格式: {ext}"

        file_size = path.stat().st_size
        if file_size > max_size:
            return False, f"文件大小超过限制: {file_size} > {max_size}"

        return True, "验证通过"

    def parse_bytes(self, file_bytes: bytes, suffix: str) -> str:
        ext = suffix.lower()
        if ext not in self.supported_extensions:
            raise ValueError(f"不支持的文件格式: {ext}")

        if ext in {".jpg", ".jpeg", ".png"}:
            image = Image.open(BytesIO(file_bytes))
            image = self._preprocess_image_for_ocr(image)
            result = self.ocr_engine.extract_text(image)
            result.text = self._normalize_ocr_text(result.text)
            assessment = self.quality_checker.assess(result.text)
            if not assessment.passed:
                raise OcrQualityError(
                    f"OCR识别结果质量不足: engine={result.engine}, score={assessment.score:.2f}, reasons={','.join(assessment.reasons)}"
                )
            return result.text.strip()

        raise ValueError("parse_bytes 目前仅支持图片文件")


def create_document_parser() -> DocumentParser:
    paddle_ocr_engine = PaddleOcrEngine()
    tesseract_ocr_engine = TesseractOcrEngine()
    ocr_engine = build_ocr_engine(paddle_ocr_engine, tesseract_ocr_engine)
    return DocumentParser(ocr_engine=ocr_engine)


document_parser = create_document_parser()
