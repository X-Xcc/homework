import urllib.request, re

headers = {"User-Agent": "Mozilla/5.0"}

# Download the full JS and search for auth/token/captcha patterns
req = urllib.request.Request(
    "https://flk.npc.gov.cn/assets/index-UYjjaqh-.js",
    headers=headers
)
js = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", errors="replace")

# Search for relevant patterns
patterns = [
    (r'captcha|verify|slider|token|xsrf|csrf|sign|encrypt', "Auth/security"),
    (r'headers\[["\']([^"\']+)["\']\]', "Header keys"),
    (r'interceptors\.request\.use', "Axios interceptors"),
    (r'baseURL[:\s]*["\']([^"\']+)["\']', "Base URL"),
]

for pattern, label in patterns:
    matches = re.findall(pattern, js, re.IGNORECASE)
    if matches:
        unique = list(set(matches))[:10]
        print(f"{label}: {unique}")

# Also look for the search function implementation
search_idx = js.find("/law-search/search/list")
if search_idx > 0:
    context = js[search_idx-200:search_idx+300]
    print(f"\nContext around search/list:")
    print(context[:600])