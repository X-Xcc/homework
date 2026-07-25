import urllib.request, urllib.error, json

BASE = "http://127.0.0.1:8000"

def api(method, path, body_data=None, token=None):
    url = BASE + path
    data = json.dumps(body_data).encode() if body_data else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req)
        raw = resp.read()
        try:
            return json.loads(raw), resp.status
        except:
            return {"_raw_len": len(raw)}, resp.status
    except urllib.error.HTTPError as e:
        err_text = e.read().decode()
        print("HTTP " + str(e.code) + ": " + err_text[:300])
        return None, e.code

# Login
result, code = api("POST", "/api/user/login", {"account": "testuser", "password": "Test12345!"})
token = result["access_token"]

# Test each export function via the actual Python module
import sys
sys.path.insert(0, "D:/homework/backend")
from app.api.export_utils import ExportRequest, _generate_txt, _generate_docx, _generate_pdf

data = ExportRequest(
    document_name="test.docx",
    summary="test",
    risks=[{"level": "high", "title": "t", "description": "d"}],
    overall_risk_level="high",
    overall_score=75,
    format="txt",
)

print("\nDirect Python test:")
for name, fn in [("txt", _generate_txt), ("docx", _generate_docx), ("pdf", _generate_pdf)]:
    try:
        buf = fn(data)
        print(f"  {name}: OK - {len(buf.getvalue())} bytes")
    except Exception as e:
        print(f"  {name}: ERROR - {e}")

# Also test the endpoint handler directly
print("\nDirect endpoint test:")
import asyncio
from app.api.document import export_report

async def test():
    from unittest.mock import MagicMock
    mock_user = MagicMock()
    mock_user.id = "test"
    try:
        resp = await export_report(data, mock_user)
        print(f"  Response type: {type(resp).__name__}")
        print(f"  Status: {resp.status_code}")
    except Exception as e:
        import traceback
        print(f"  ERROR: {e}")
        traceback.print_exc()

asyncio.run(test())