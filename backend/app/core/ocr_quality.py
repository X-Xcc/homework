from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class OcrQualityAssessment:
    passed: bool
    score: float
    reasons: list[str]


class OcrQualityChecker:
    def assess(self, text: str) -> OcrQualityAssessment:
        normalized = (text or "").strip()
        reasons: list[str] = []

        if not normalized:
            reasons.append("empty_text")
            return OcrQualityAssessment(False, 0.0, reasons)

        length = len(normalized)
        chinese_chars = sum(1 for ch in normalized if "\u4e00" <= ch <= "\u9fff")
        digits = sum(1 for ch in normalized if ch.isdigit())
        alpha = sum(1 for ch in normalized if ch.isalpha())
        weird = sum(1 for ch in normalized if ch in "?？�")
        replacement_like = sum(1 for ch in normalized if ord(ch) == 65533)
        greek_cyrillic = sum(1 for ch in normalized if ("\u0370" <= ch <= "\u03ff") or ("\u0400" <= ch <= "\u04ff"))
        box_drawing = sum(1 for ch in normalized if "\u2500" <= ch <= "\u257f")

        chinese_ratio = chinese_chars / length if length else 0.0
        weird_ratio = weird / length if length else 0.0
        digit_ratio = digits / length if length else 0.0
        alpha_ratio = alpha / length if length else 0.0
        replacement_ratio = replacement_like / length if length else 0.0
        foreign_symbol_ratio = (greek_cyrillic + box_drawing) / length if length else 0.0

        repeated_run = self._max_repeated_char_run(normalized)

        score = 1.0
        if length < 20:
            reasons.append("too_short")
            score -= 0.35
        if chinese_chars > 0 and chinese_ratio < 0.2:
            reasons.append("low_chinese_ratio")
            score -= 0.25
        if weird_ratio > 0.05:
            reasons.append("too_many_weird_chars")
            score -= 0.3
        if digit_ratio > 0.6 and alpha_ratio < 0.2 and chinese_ratio < 0.1:
            reasons.append("digit_heavy_noise")
            score -= 0.3
        if repeated_run >= 6:
            reasons.append("repeated_char_noise")
            score -= 0.25
        if replacement_ratio > 0.01:
            reasons.append("replacement_char_noise")
            score -= 0.35
        if foreign_symbol_ratio > 0.08:
            reasons.append("encoding_garbled_text")
            score -= 0.45

        blocking_reasons = {
            "empty_text",
            "too_many_weird_chars",
            "digit_heavy_noise",
            "replacement_char_noise",
            "encoding_garbled_text",
        }
        passed = score >= 0.55 and not any(reason in blocking_reasons for reason in reasons)
        return OcrQualityAssessment(passed, max(0.0, score), reasons)

    def _max_repeated_char_run(self, text: str) -> int:
        current = 0
        max_run = 0
        last = ""

        for ch in text:
            if ch == last:
                current += 1
            else:
                current = 1
                last = ch
            max_run = max(max_run, current)

        return max_run
