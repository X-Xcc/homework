import json, os

kb_dir = r"D:\homework\backend\data\knowledge_base"
total = 0
for f in sorted(os.listdir(kb_dir)):
    if f.endswith(".json"):
        path = os.path.join(kb_dir, f)
        with open(path, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        print(f"{f}: {len(data)} articles")
        total += len(data)
        # Show first article
        if data:
            a = data[0]
            print(f"  Sample: [{a.get('category','')}] {a.get('law_name','')} {a.get('article_number','')}: {a.get('title','')}")
            print(f"  Content: {a.get('content','')[:100]}...")
            if "keywords" in a:
                print(f"  Keywords: {a['keywords']}")
        print()

print(f"Total: {total} articles")