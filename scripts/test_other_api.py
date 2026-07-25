import urllib.request, json

BASE = "https://flk.npc.gov.cn"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://flk.npc.gov.cn/",
    "Origin": "https://flk.npc.gov.cn",
    "Content-Type": "application/json",
    "isToken": "false",
}

# Try fljc endpoint
url = BASE + "/law-search/index/fljc"
data = {"keyword": "民法典"}
body = json.dumps(data).encode()
req = urllib.request.Request(url, data=body, headers=headers, method="POST")
try:
    resp = urllib.request.urlopen(req, timeout=15)
    result = json.loads(resp.read().decode())
    print(f"fljc: {json.dumps(result, ensure_ascii=False)[:500]}")
except Exception as e:
    print(f"fljc error: {e}")
    if hasattr(e, 'read'):
        print(e.read().decode()[:500])

# Try recommend endpoint
print("\n--- recommend ---")
url2 = BASE + "/law-search/search/recommend?keyword=民法典"
req2 = urllib.request.Request(url2, headers=headers)
try:
    resp2 = urllib.request.urlopen(req2, timeout=15)
    result2 = json.loads(resp2.read().decode())
    print(f"recommend: {json.dumps(result2, ensure_ascii=False)[:500]}")
except Exception as e:
    print(f"recommend error: {e}")
    if hasattr(e, 'read'):
        print(e.read().decode()[:500])

# Try aggregate data
print("\n--- aggregate ---")
url3 = BASE + "/law-search/index/aggregateData"
req3 = urllib.request.Request(url3, headers=headers)
try:
    resp3 = urllib.request.urlopen(req3, timeout=15)
    result3 = json.loads(resp3.read().decode())
    print(f"aggregate: {json.dumps(result3, ensure_ascii=False)[:500]}")
except Exception as e:
    print(f"aggregate error: {e}")
    if hasattr(e, 'read'):
        print(e.read().decode()[:500])