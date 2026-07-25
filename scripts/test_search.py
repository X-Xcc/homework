import sys
sys.path.insert(0, r"D:\homework\backend")
from app.core.legal_db import legal_db, _tokenize

# Test some common queries
test_queries = [
    "合同违约",
    "格式条款",
    "个人信息保护",
    "违约责任",
    "劳动法",
    "知识产权",
    "数据安全",
    "公司法",
    "刑法 诈骗",
    "合同纠纷",
    "损害赔偿",
    "隐私权",
    "消费者权益",
    "劳动合同",
]

for q in test_queries:
    print(f"\n=== Query: {q} ===")
    print(f"  Tokens: {_tokenize(q)[:10]}...")
    results = legal_db.search(q, limit=5)
    for i, r in enumerate(results):
        print(f"  {i+1}. [{r.law_name}] {r.article_number} {r.title or ''}: {r.content[:60]}...")