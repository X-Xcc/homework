from __future__ import annotations

from PIL import Image

from app.core.document_parser import DocumentParser
from app.core.ocr_base import OcrEngine
from app.core.ocr_quality import OcrQualityChecker
from app.core.ocr_router import OcrEngineRouter
from app.core.ocr_types import OcrExecutionError, OcrResult


class StubOcrEngine(OcrEngine):
    engine_name = "stub"

    def __init__(self, text: str):
        self.text = text

    def is_available(self) -> bool:
        return True

    def extract_text(self, image):
        return OcrResult(text=self.text, engine=self.engine_name)


class NamedStubOcrEngine(OcrEngine):
    def __init__(self, name: str, text: str):
        self.engine_name = name
        self.text = text

    def is_available(self) -> bool:
        return True

    def extract_text(self, image):
        return OcrResult(text=self.text, engine=self.engine_name)


class FailingStubOcrEngine(OcrEngine):
    engine_name = "failing"

    def is_available(self) -> bool:
        return True

    def extract_text(self, image):
        raise OcrExecutionError("boom")


class GarbledStubOcrEngine(OcrEngine):
    engine_name = "garbled"

    def is_available(self) -> bool:
        return True

    def extract_text(self, image):
        return OcrResult(text="�� �� �� :_____, �� �� �� �� �� ��", engine=self.engine_name)



def test_quality_checker_accepts_meaningful_chinese_text(tmp_path):
    parser = DocumentParser(ocr_engine=StubOcrEngine("甲方应当在五个工作日内支付合同款项，逾期应承担违约责任。"))
    image_path = tmp_path / "contract.png"
    Image.new("RGB", (100, 100), color="white").save(image_path)
    text = parser.parse(str(image_path))
    assert "甲方" in text



def test_quality_checker_rejects_garbled_text(tmp_path):
    parser = DocumentParser(ocr_engine=StubOcrEngine("222222??????"))
    image_path = tmp_path / "garbled.png"
    Image.new("RGB", (100, 100), color="white").save(image_path)

    try:
        parser.parse(str(image_path))
    except Exception as exc:
        assert "质量不足" in str(exc)
    else:
        raise AssertionError("Expected OCR quality failure")



def test_quality_checker_rejects_encoding_garbled_text():
    assessment = OcrQualityChecker().assess("�� �� �� :_____, �� �� �� �� �� ��")
    assert not assessment.passed
    assert "encoding_garbled_text" in assessment.reasons or "replacement_char_noise" in assessment.reasons



def test_router_falls_back_when_primary_raises(tmp_path):
    router = OcrEngineRouter(
        primary_engine=FailingStubOcrEngine(),
        fallback_engines=[NamedStubOcrEngine("tesseract", "本合同自双方签字盖章之日起生效，任何争议应协商解决。")],
    )
    parser = DocumentParser(ocr_engine=router)
    image_path = tmp_path / "fallback-success.png"
    Image.new("RGB", (120, 120), color="white").save(image_path)

    text = parser.parse(str(image_path))
    assert "签字盖章" in text



def test_router_falls_back_when_primary_result_is_low_quality(tmp_path):
    router = OcrEngineRouter(
        primary_engine=GarbledStubOcrEngine(),
        fallback_engines=[NamedStubOcrEngine("tesseract", "乙方应于收到通知后三日内完成整改，否则承担违约责任。")],
    )
    parser = DocumentParser(ocr_engine=router)
    image_path = tmp_path / "fallback-quality.png"
    Image.new("RGB", (120, 120), color="white").save(image_path)

    text = parser.parse(str(image_path))
    assert "整改" in text
