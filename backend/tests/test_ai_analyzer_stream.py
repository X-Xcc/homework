import json

from app.core.ai_analyzer import ai_analyzer


def test_ai_analyzer_exposes_contract_stream_method():
    assert hasattr(ai_analyzer, "analyze_contract_stream")


def test_ai_analyzer_stream_parser_handles_json_fences():
    content = """```json
{
  \"risks\": [],
  \"summary\": \"ok\"
}
```"""

    parsed = ai_analyzer._parse_json(content)

    assert parsed == {"risks": [], "summary": "ok"}
