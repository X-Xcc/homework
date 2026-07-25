import urllib.request, re

headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://flk.npc.gov.cn/"}

# 1. Get the main page to find JS asset path
req = urllib.request.Request("https://flk.npc.gov.cn/", headers=headers)
html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8")
# Find the JS bundle
js_match = re.search(r'src="(/assets/[^"]+\.js)"', html)
if js_match:
    js_path = js_match.group(1)
    print(f"JS: {js_path}")
    
    # 2. Download the JS bundle
    js_url = "https://flk.npc.gov.cn" + js_path
    req2 = urllib.request.Request(js_url, headers=headers)
    js_content = urllib.request.urlopen(req2, timeout=30).read().decode("utf-8", errors="replace")
    print(f"JS size: {len(js_content)} bytes")
    
    # 3. Search for API endpoints in the JS bundle
    api_patterns = re.findall(r'(?:url|path|baseURL|api)["\']?\s*[:=]\s*["\']([^"\']{3,80})["\']', js_content)
    api_urls = re.findall(r'["\'](/[a-z]+/[a-z]+[^"\']{2,80})["\']', js_content)
    all_api = re.findall(r'["\']([^"\']*(?:api|search|law|data|list)[^"\']*)["\']', js_content, re.IGNORECASE)
    
    print(f"\nAPI patterns: {api_patterns[:20]}")
    print(f"\nAPI URLs: {api_urls[:20]}")
    print(f"\nAll API-related: {all_api[:20]}")
else:
    print("No JS found in HTML")
    print("HTML:", html[:500])