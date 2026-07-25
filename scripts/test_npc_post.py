import urllib.request, urllib.parse, json, time

BASE = "https://flk.npc.gov.cn"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://flk.npc.gov.cn/",
    "Origin": "https://flk.npc.gov.cn",
    "Content-Type": "application/json",
}

def post(path, data):
    url = BASE + path
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        raw = resp.read().decode("utf-8")
        return json.loads(raw)
    except Exception as e:
        return {"error": str(e)}

# Try different body formats
tries = [
    # Simple keyword search
    {"keyword": "民法典", "page": 1, "size": 3},
    # With more fields
    {"keyword": "民法典", "pageNum": 1, "pageSize": 3},
    # As query params in body
    {"searchWord": "民法典", "current": 1, "size": 3},
]

for i, data in enumerate(tries):
    result = post("/law-search/search/list", data)
    print(f"Try {i+1} {data}: {json.dumps(result, ensure_ascii=False)[:300]}")
    time.sleep(0.3)

# Also try the details endpoint
result2 = post("/law-search/search/enumData", {})
print(f"\nEnumData: {json.dumps(result2, ensure_ascii=False)[:500]}")