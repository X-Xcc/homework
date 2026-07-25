import urllib.request, urllib.parse, json, time

BASE = "https://flk.npc.gov.cn"

def api(path, params=None):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": "https://flk.npc.gov.cn/",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        raw = resp.read().decode("utf-8")
        return json.loads(raw)
    except Exception as e:
        return {"error": str(e)}

# 1. Search for common laws
laws_to_search = [
    "中华人民共和国民法典",
    "中华人民共和国刑法",
    "中华人民共和国劳动合同法",
    "中华人民共和国公司法",
    "中华人民共和国证券法",
    "中华人民共和国个人信息保护法",
    "中华人民共和国数据安全法",
    "中华人民共和国反垄断法",
    "中华人民共和国著作权法",
    "中华人民共和国专利法",
    "中华人民共和国商标法",
    "中华人民共和国劳动法",
    "中华人民共和国环境保护法",
    "中华人民共和国消费者权益保护法",
]

for law_name in laws_to_search:
    result = api("/api/search", {"keyword": law_name, "size": 1})
    if "error" not in result and result.get("data"):
        items = result.get("data", {}).get("items", []) or result.get("data", [])
        if items:
            item = items[0]
            print(f"  {law_name}: found, id={item.get('id','')[:30]}")
        else:
            print(f"  {law_name}: no results")
    else:
        print(f"  {law_name}: API error - {str(result)[:100]}")
    time.sleep(0.3)