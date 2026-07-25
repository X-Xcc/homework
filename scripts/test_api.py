import urllib.request, json

def api(path):
    url = "http://127.0.0.1:8000" + path
    resp = urllib.request.urlopen(url)
    return json.loads(resp.read())

for q in ["格式条款", "合同违约", "个人信息保护", "数据出境"]:
    encoded = urllib.parse.quote(q)
    results = api(f"/api/search/law?q={encoded}&limit=3")
    print(f"\n=== {q} ({len(results)} results) ===")
    for r in results:
        print(f"  [{r['law_name']}] {r['article_number']} {r.get('title','')}")