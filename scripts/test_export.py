import urllib.request, urllib.error, json, sys

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
        code = resp.status
        try:
            return json.loads(raw), code
        except:
            return {"_raw": raw}, code
    except urllib.error.HTTPError as e:
        err_text = e.read().decode()
        print("  HTTP " + str(e.code) + ": " + err_text[:200])
        return None, e.code

# Login
print("1. Login as testuser...")
result, code = api("POST", "/api/user/login", {"account": "testuser", "password": "Test12345!"})
if code != 200:
    print("Login failed, trying to register...")
    result2, code2 = api("POST", "/api/user/register", 
        {"username": "export_test", "password": "Export12345!", "email": "exp2@test.com"})
    if code2 in (200, 201):
        result, code = api("POST", "/api/user/login", {"account": "export_test", "password": "Export12345!"})
    else:
        print("Cannot proceed")
        sys.exit(1)

token = result.get("access_token", "")
print("  Token: " + token[:30] + "...")

# Test export
print("\n2. Test export endpoint...")
for fmt in ["txt", "docx", "pdf"]:
    body = {
        "document_name": "test.docx",
        "summary": "test summary",
        "risks": [{"level": "high", "title": "test risk", "description": "test desc"}],
        "overall_risk_level": "high",
        "overall_score": 75,
        "format": fmt,
    }
    result, code = api("POST", "/api/document/export", body, token=token)
    if code == 200:
        print("  " + fmt + ": SUCCESS")
    else:
        print("  " + fmt + ": FAILED")

print("\nDone!")