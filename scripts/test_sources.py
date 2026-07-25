import urllib.request, json

# Try gov.cn / pkulaw / other open legal sources
test_urls = [
    "https://api.pkulaw.com/law",
    "https://www.gov.cn/api/search",
    "http://www.npc.gov.cn",
]

for url in test_urls:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}, method="HEAD")
        resp = urllib.request.urlopen(req, timeout=8)
        print(f"{url}: HTTP {resp.status}")
    except Exception as e:
        print(f"{url}: {type(e).__name__}")

# Try a more direct approach - legal texts from GitHub
import urllib.request
print("\nTrying GitHub open-source legal datasets...")
github_urls = [
    "https://raw.githubusercontent.com/LawRefBook/Laws/master/README.md",
]

for url in github_urls:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        print(f"{url}: OK, {len(resp.read())} bytes")
    except Exception as e:
        print(f"{url}: {type(e).__name__}")