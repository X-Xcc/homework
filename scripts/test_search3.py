import sys
sys.path.insert(0, r"D:\homework\backend")
from app.core.legal_db import legal_db, _tokenize

queries = [
    "合同违约", "格式条款", "个人信息保护", "违约责任",
    "劳动合同", "合同法", "消费者权益", "数据出境", "竞业限制",
]

for q in queries:
    print(f"\n=== {q}  Tokens: {_tokenize(q)} ===")
    results = legal_db.search(q, limit=3)
    for i, r in enumerate(results):
        print(f"  {i+1}. [{r.law_name}] {r.article_number} {r.title or ''}")