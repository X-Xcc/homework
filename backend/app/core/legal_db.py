import json
import re
from pathlib import Path
from typing import List, Optional, Dict, Set
from collections import defaultdict
import jieba
import math

from app.config import settings
from app.models.schemas import LawArticle

KB_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "knowledge_base"

# ── jieba configuration ──
jieba.setLogLevel(20)  # suppress jieba debug output

# Pre-build a legal domain dictionary from known terms
LEGAL_TERMS = [
    "格式条款", "违约责任", "个人信息", "数据安全", "知识产权",
    "商业秘密", "不正当竞争", "不可抗力", "损害赔偿", "惩罚性赔偿",
    "连带责任", "诉讼时效", "管辖权", "仲裁协议", "法人人格否认",
    "刺破公司面纱", "上市公司", "独立董事", "实际控制人", "关联交易",
    "解除合同", "继续履行", "采取补救措施", "赔偿损失", "定金罚则",
    "情势变更", "合同目的", "根本违约", "预期违约", "同时履行抗辩权",
    "不安抗辩权", "先履行抗辩权", "代位权", "撤销权", "解除权",
    "个人信息处理者", "敏感个人信息", "单独同意", "数据出境",
    "生成式人工智能", "深度合成", "算法推荐", "自动化决策",
    "劳动者", "用人单位", "劳动合同", "竞业限制", "经济补偿金",
    "工伤保险", "消费者权益", "七日无理由退货", "欺诈", "虚假宣传",
    "垄断", "经营者集中", "滥用市场支配地位", "横向垄断协议",
    "非法占有", "合同诈骗", "职务侵占", "挪用资金", "商业贿赂",
    "内幕交易", "操纵市场", "信息披露", "强制要约收购",
    "GDPR", "CCPA", "数据保护官", "数据保护影响评估",
    "建筑工程", "施工许可", "竣工验收", "质量保修",
    "医疗损害", "医疗事故", "知情同意", "病历资料",
    "环境污染", "生态破坏", "环境公益诉讼", "排污许可",
    "行政处罚", "行政许可", "行政复议", "行政诉讼",
    "善意取得", "无权处分", "表见代理", "不当得利", "无因管理",
    "保证合同", "抵押", "质押", "留置", "定金",
]
for term in LEGAL_TERMS:
    jieba.add_word(term)



def _tokenize(text: str) -> List[str]:
    """Jieba-based Chinese word segmentation. Single CJK chars excluded to reduce noise."""
    text = text.lower()
    tokens = [t.strip() for t in jieba.cut(text) if t.strip()]
    words = set()
    for t in tokens:
        has_cjk = bool(re.search(r'[\u4e00-\u9fff]', t))
        is_alnum = bool(re.match(r'^[a-z0-9]+$', t))
        if has_cjk and len(t) >= 2:
            words.add(t)
        elif is_alnum and len(t) >= 2:
            words.add(t)
    return list(words)

class LegalDatabase:
    def __init__(self):
        self._articles: List[dict] = []
        self._index: Dict[str, Set[int]] = defaultdict(set)
        self._id_index: Dict[str, dict] = {}
        self._category_index: Dict[str, List[int]] = defaultdict(list)
        # TF-IDF
        self._doc_freq: Dict[str, int] = defaultdict(int)  # token -> num docs containing it
        self._doc_count: int = 0
        self.load_data()

    def load_data(self):
        self._articles.clear()
        self._index.clear()
        self._id_index.clear()
        self._category_index.clear()
        self._doc_freq.clear()
        self._doc_count = 0

        if KB_DIR.exists():
            for json_file in sorted(KB_DIR.glob("*.json")):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        batch = json.load(f)
                    for article in batch:
                        idx = len(self._articles)
                        self._articles.append(article)
                        aid = article.get("id", "")
                        if aid:
                            self._id_index[aid] = article
                        cat = article.get("category", "")
                        if cat:
                            self._category_index[cat].append(idx)
                        searchable = self._get_searchable_text(article)
                        tokens = _tokenize(searchable)
                        for token in set(tokens):
                            self._index[token].add(idx)
                            self._doc_freq[token] += 1
                except Exception as e:
                    print(f"Warning: failed to load {json_file.name}: {e}")

        if not self._articles:
            self._load_legacy()

        self._doc_count = len(self._articles)

        print(f"LegalDatabase: loaded {self._doc_count} articles, "
              f"{len(self._id_index)} indexed IDs, {len(self._category_index)} categories, "
              f"{len(self._index)} unique tokens")

    def _load_legacy(self):
        for path, name in [
            (settings.CRIMINAL_LAW_PATH, "\u5211\u6cd5"),
            (settings.CIVIL_LAW_PATH, "\u6c11\u6cd5\u5178"),
        ]:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    batch = json.load(f)
                for article in batch:
                    article["category"] = article.get("category", name)
                    idx = len(self._articles)
                    self._articles.append(article)
                    aid = article.get("id", "")
                    if aid:
                        self._id_index[aid] = article
                    searchable = self._get_searchable_text(article)
                    for token in set(_tokenize(searchable)):
                        self._index[token].add(idx)
                        self._doc_freq[token] += 1
            except FileNotFoundError:
                pass
        self._doc_count = len(self._articles)

    def _get_searchable_text(self, item: dict) -> str:
        return (
            f"{item.get('law_name', '')} "
            f"{item.get('article_number', '')} "
            f"{item.get('title', '')} "
            f"{item.get('content', '')} "
            + " ".join(item.get("keywords", []))
        )

    def _tfidf(self, token: str) -> float:
        """Inverse document frequency for a token."""
        df = self._doc_freq.get(token, 0)
        if df == 0 or self._doc_count == 0:
            return 0.0
        return math.log((self._doc_count + 1) / (df + 1))

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 20,
    ) -> List[LawArticle]:
        query = query.strip()

        # Narrow candidate pool by category
        if category and category in self._category_index:
            candidate_indices = set(self._category_index[category])
        else:
            candidate_indices = set(range(len(self._articles)))

        if not query:
            results = []
            for idx in sorted(candidate_indices)[:limit]:
                results.append(self._to_article(self._articles[idx]))
            return results

        query_tokens = _tokenize(query)
        if not query_tokens:
            return []

        # ── TF-IDF weighted scoring ──
        scores: Dict[int, float] = defaultdict(float)
        query_lower = query.lower()

        # Count query token frequencies for TF
        qt_counts: Dict[str, int] = defaultdict(int)
        for t in query_tokens:
            qt_counts[t] += 1

        for token, qt_count in qt_counts.items():
            idf = self._tfidf(token)
            tf = qt_count  # term frequency in query
            weight = tf * idf
            for idx in self._index.get(token, set()):
                if idx in candidate_indices:
                    scores[idx] += weight

        # ── Exact/Substring match bonus (capped) ──
        for idx in list(candidate_indices):
            searchable = self._get_searchable_text(self._articles[idx]).lower()
            # Exact phrase match
            if query_lower in searchable:
                scores[idx] += 3.0
            # Title exact match
            title = (self._articles[idx].get("title") or "").lower()
            if query_lower in title:
                scores[idx] += 5.0
            # Article number match
            art_no = (self._articles[idx].get("article_number") or "").lower()
            if query_lower in art_no:
                scores[idx] += 5.0

        # ── Rank and return ──
        ranked = sorted(scores.items(), key=lambda x: -x[1])

        return [self._to_article(self._articles[idx]) for idx, _ in ranked[:limit]]

    def _to_article(self, item: dict) -> LawArticle:
        return LawArticle(
            id=item.get("id", ""),
            law_name=item.get("law_name", ""),
            chapter=item.get("chapter"),
            article_number=item.get("article_number", ""),
            title=item.get("title"),
            content=item.get("content", ""),
            judicial_interpretations=item.get("judicial_interpretations", []),
            related_cases=item.get("related_cases", []),
        )

    def get_by_id(self, article_id: str) -> Optional[LawArticle]:
        item = self._id_index.get(article_id)
        if item:
            return self._to_article(item)
        return None

    def get_by_category(self, category: str) -> List[LawArticle]:
        indices = self._category_index.get(category, [])
        return [self._to_article(self._articles[idx]) for idx in indices]

    def list_categories(self) -> List[str]:
        return sorted(self._category_index.keys())

    @property
    def total_articles(self) -> int:
        return len(self._articles)


legal_db = LegalDatabase()