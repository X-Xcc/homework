from __future__ import annotations

from app.core.document_parser import DocumentParser
from app.core.ocr import PaddleOcrEngine, TesseractOcrEngine, build_ocr_engine

paddle_ocr_engine = PaddleOcrEngine()
tesseract_ocr_engine = TesseractOcrEngine()
ocr_engine = build_ocr_engine(paddle_ocr_engine, tesseract_ocr_engine)
document_parser = DocumentParser(ocr_engine=ocr_engine)
