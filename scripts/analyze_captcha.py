import urllib.request, re

headers = {"User-Agent": "Mozilla/5.0"}
req = urllib.request.Request(
    "https://flk.npc.gov.cn/assets/index-UYjjaqh-.js",
    headers=headers
)
js = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", errors="replace")

# Find captcha/slider related code
for keyword in ["captcha", "slider", "verify", "checkToken"]:
    idx = js.lower().find(keyword.lower())
    if idx > 0:
        print(f"\n=== {keyword} at {idx} ===")
        print(js[idx-100:idx+300])
        print()

# Find the axios/interceptor setup
idx2 = js.find("interceptors.request.use")
if idx2 > 0:
    print(f"\n=== interceptor ===")
    print(js[idx2:idx2+500])