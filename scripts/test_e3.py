import urllib.request, urllib.error, json, sys

BASE = "http://127.0.0.1:8000"

def api(m, p, b=None, t=None):
    u = BASE + p
    d = json.dumps(b).encode() if b else None
    h = {"Content-Type": "application/json"}
    if t: h["Authorization"] = "Bearer " + t
    rq = urllib.request.Request(u, data=d, headers=h, method=m)
    try:
        rs = urllib.request.urlopen(rq)
        rw = rs.read()
        return {"ok": True, "raw": rw, "ct": rs.headers.get("Content-Type",""), "cd": rs.headers.get("Content-Disposition",""), "status": rs.status}
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": e.read().decode(), "status": e.code}

user = "exptest_final"
print("Registering " + user + "...")
r = api("POST", "/api/user/register", {"username": user, "password": "Pass12345!", "email": user + "@test.com"})
r = api("POST", "/api/user/login", {"account": user, "password": "Pass12345!"})
if not r["ok"]:
    print("Login failed: " + r["error"])
    sys.exit(1)
token = json.loads(r["raw"])["access_token"]
print("Login OK")

body = {"document_name": "test.docx", "summary": "test", "risks": [{"level": "high", "title": "t", "description": "d"}], "overall_risk_level": "high", "overall_score": 75}
for fmt in ["txt", "docx", "pdf"]:
    body["format"] = fmt
    r = api("POST", "/api/document/export", body, token)
    if r["ok"]:
        cd = r.get("cd", "")
        print(fmt + ": OK - " + str(len(r["raw"])) + " bytes, CD: " + cd[:60])
    else:
        print(fmt + ": FAIL " + str(r["status"]) + " - " + r["error"][:200])
print("Done!")