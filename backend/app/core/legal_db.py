import json
from typing import List, Optional
from app.config import settings
from app.models.schemas import LawArticle

class LegalDatabase:
    def __init__(self):
        self.criminal_law: List[dict] = []
        self.civil_law: List[dict] = []
        self.load_data()

    def load_data(self):
        try:
            with open(settings.CRIMINAL_LAW_PATH, "r", encoding="utf-8") as f:
                self.criminal_law = json.load(f)
        except FileNotFoundError:
            self.criminal_law = []

        try:
            with open(settings.CIVIL_LAW_PATH, "r", encoding="utf-8") as f:
                self.civil_law = json.load(f)
        except FileNotFoundError:
            self.civil_law = []

    def search(self, query: str, law_type: Optional[str] = None, limit: int = 20) -> List[LawArticle]:
        results = []
        query = query.lower()

        datasets = []
        if law_type == "criminal":
            datasets = [("刑法", self.criminal_law)]
        elif law_type == "civil":
            datasets = [("民法典", self.civil_law)]
        else:
            datasets = [("刑法", self.criminal_law), ("民法典", self.civil_law)]

        for law_name, data in datasets:
            for item in data:
                if self._matches(item, query):
                    results.append(LawArticle(
                        id=item.get("id", ""),
                        law_name=law_name,
                        chapter=item.get("chapter"),
                        article_number=item.get("article_number", ""),
                        title=item.get("title"),
                        content=item.get("content", ""),
                        judicial_interpretations=item.get("judicial_interpretations", []),
                        related_cases=item.get("related_cases", [])
                    ))
                    if len(results) >= limit:
                        return results

        return results

    def _matches(self, item: dict, query: str) -> bool:
        if not query:
            return True
        searchable = f"{item.get('article_number', '')} {item.get('title', '')} {item.get('content', '')} {item.get('crime_name', '')}".lower()
        return query in searchable

    def get_by_id(self, article_id: str) -> Optional[LawArticle]:
        for item in self.criminal_law:
            if item.get("id") == article_id:
                return LawArticle(
                    id=item["id"],
                    law_name="刑法",
                    chapter=item.get("chapter"),
                    article_number=item.get("article_number", ""),
                    title=item.get("title"),
                    content=item.get("content", ""),
                    judicial_interpretations=item.get("judicial_interpretations", []),
                    related_cases=item.get("related_cases", [])
                )
        for item in self.civil_law:
            if item.get("id") == article_id:
                return LawArticle(
                    id=item["id"],
                    law_name="民法典",
                    chapter=item.get("chapter"),
                    article_number=item.get("article_number", ""),
                    title=item.get("title"),
                    content=item.get("content", ""),
                    judicial_interpretations=item.get("judicial_interpretations", []),
                    related_cases=item.get("related_cases", [])
                )
        return None

legal_db = LegalDatabase()
