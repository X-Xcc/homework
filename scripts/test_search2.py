import sys
sys.path.insert(0, r"D:\homework\backend")
from app.core.legal_db import legal_db, _tokenize

test_queries = [
    "合同违约",
    "格式条款",
    "个人信息保护",
    "违约责任",
    "劳动合同",
    "隐私权",
    "合同法",
    "消费者权益",
    "损害赔偿",
    "知识产权",
    "数据出境",
    "竞业限制",
]

for q in test_queries:
    print(f"\n{'='*60}")
    print(f"  Query: {q}")
    print(f"  Tokens: {_tokenize(q)}")
    results = legal_db.search(q, limit=5)
    for i, r in enumerate(results):
        cat = r.law_name or ""
        title = r.title or ""
        print(f"  {i+1}. [{cat}] {r.article_number} {title}")
        print(f"     {r.content[:80]}...")