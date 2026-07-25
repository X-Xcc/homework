import urllib.request, json

# Try the NPC official legal database
urls = [
    "https://flk.npc.gov.cn/api/search",
    "https://flk.npc.gov.cn",
]

for url in urls:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        print(f"{url}: HTTP {resp.status}, size={len(resp.read())}")
    except Exception as e:
        print(f"{url}: {e}")