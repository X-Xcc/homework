import urllib.request, urllib.parse, json, time

BASE = "https://flk.npc.gov.cn"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://flk.npc.gov.cn/",
    "Origin": "https://flk.npc.gov.cn",
}

# Try the search API
params = {
    "page": "1",
    "size": "5",
    "keyword": "民法典",
}
url = BASE + "/law-search/search/list?" + urllib.parse.urlencode(params)
print(f"Trying: {url}")
try:
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=15)
    raw = resp.read().decode("utf-8")
    data = json.loads(raw)
    print(f"Status: {resp.status}")
    print(f"Keys: {list(data.keys()) if isinstance(data, dict) else 'not dict'}")
    print(json.dumps(data, ensure_ascii=False, indent=2)[:1000])
except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, 'read'):
        print(f"Body: {e.read().decode('utf-8', errors='replace')[:500]}")