from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.document_service import document_parser


def summarize_text(text: str) -> dict:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return {
        "char_count": len(text),
        "line_count": len(lines),
        "preview": lines[:8],
    }


def main() -> None:
    uploads = ROOT / "uploads"
    samples = [uploads / "sample-1.png", uploads / "sample-2.png"]
    result: dict[str, dict] = {}

    for sample in samples:
        try:
            text = document_parser.parse(str(sample))
            result[sample.name] = {
                "status": "ok",
                "summary": summarize_text(text),
            }
        except Exception as exc:
            result[sample.name] = {
                "status": "error",
                "error": str(exc),
            }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
