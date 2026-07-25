import urllib.request, json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml",
}

# Get the main page to understand the structure
req = urllib.request.Request("https://flk.npc.gov.cn/", headers=headers)
resp = urllib.request.urlopen(req, timeout=15)
html = resp.read().decode("utf-8", errors="replace")

# Look for API endpoints in the HTML
import re
api_patterns = re.findall(r'(/api/[^\s"\']+)', html)
js_patterns = re.findall(r'(https?://[^\s"\']+\.js)', html)
print("API patterns:", api_patterns[:10])
print("JS files:", js_patterns[:10])

# Also try the search page directly
req2 = urllib.request.Request(
    "https://flk.npc.gov.cn/api/search?keyword=%E6%B0%91%E6%B3%95%E5%85%B8&size=1",
    headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json, text/plain, */*",
             "Referer": "https://flk.npc.gov.cn/"}
)
resp2 = urllib.request.urlopen(req2, timeout=15)
raw = resp2.read()
print(f"\nSearch API status: {resp2.status}, size: {len(raw)}")
print(f"Response: {raw[:500]}")