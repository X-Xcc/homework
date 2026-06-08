from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class LawArticle(BaseModel):
    id: str
    law_name: str
    chapter: Optional[str] = None
    article_number: str
    title: Optional[str] = None
    content: str
    judicial_interpretations: Optional[List[str]] = []
    related_cases: Optional[List[str]] = []

class DocumentUpload(BaseModel):
    filename: str
    file_type: str
    file_size: int

class AnalysisResult(BaseModel):
    id: str
    document_name: str
    status: AnalysisStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    risks: List["RiskItem"] = []
    summary: Optional[str] = None

class RiskItem(BaseModel):
    id: str
    level: RiskLevel
    title: str
    description: str
    location: Optional[str] = None
    legal_basis: List[str] = []
    suggestion: Optional[str] = None

class ComparisonResult(BaseModel):
    id: str
    document_a: str
    document_b: str
    created_at: datetime
    changes: List["ChangeItem"] = []
    summary: Optional[str] = None

class ChangeItem(BaseModel):
    type: str
    original: Optional[str] = None
    modified: Optional[str] = None
    location: Optional[str] = None

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatSession(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessage] = []
    context: Optional[str] = None

class ContractTemplate(BaseModel):
    id: str
    name: str
    category: str
    description: Optional[str] = None
    usage_count: int = 0
    file_path: str

class UserProfile(BaseModel):
    id: str
    nickname: str
    avatar: Optional[str] = None
    analysis_count: int = 0
    chat_count: int = 0
    created_at: datetime

class FavoriteItem(BaseModel):
    id: str
    user_id: str
    item_type: str
    item_id: str
    created_at: datetime

class HistoryItem(BaseModel):
    id: str
    user_id: str
    type: str
    title: str
    created_at: datetime
    item_id: str
