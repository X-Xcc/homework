import urllib.request
import urllib.error  
import json

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
        ct = resp.headers.get("Content-Type", "")
        cd = resp.headers.get("Content-Disposition", "")
        return {"len": len(raw), "ct": ct, "cd": cd}, resp.status
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()}, e.code

result, code = api("POST", "/api/user/login", {"account": "testuser", "password": "Test12345!"})
if code != 200:
    api("POST", "/api/user/register", {"username": "exp_t2", "password": "Exp12345!", "email": "e4@t.com"})
    result, code = api("POST", "/api/user/login", {"account": "exp_t2", "password": "Exp12345!"})
token = result["access_token"]
print("Login OK")

body = {
    "document_name": "test.docx",
    "summary": "test",
    "risks": [{"level": "high", "title": "t", "description": "d"}],
    "overall_risk_level": "high",
    "overall_score": 75,
}
for fmt in ["txt", "docx", "pdf"]:
    body["format"] = fmt
    r, c = api("POST", "/api/document/export", body, token=token)
    if c == 200:
        print("  " + fmt + ": OK - " + str(r["len"]) + " bytes")
    else:
        err = r.get("error", "")
        print("  " + fmt + ": FAIL " + str(c) + " - " + err[:200])
print("Done!")