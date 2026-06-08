from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON, Boolean, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import uuid

from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

def generate_id():
    return str(uuid.uuid4())

class UserDB(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_id)
    openid = Column(String, unique=True, index=True)
    nickname = Column(String)
    avatar = Column(String)
    phone = Column(String)
    analysis_count = Column(Integer, default=0)
    chat_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AnalysisDB(Base):
    __tablename__ = "analyses"

    id = Column(String, primary_key=True, default=generate_id)
    user_id = Column(String, ForeignKey("users.id"))
    document_name = Column(String)
    document_path = Column(String)
    status = Column(String, default="pending")
    risks = Column(JSON, default=list)
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

class ComparisonDB(Base):
    __tablename__ = "comparisons"

    id = Column(String, primary_key=True, default=generate_id)
    user_id = Column(String, ForeignKey("users.id"))
    document_a = Column(String)
    document_b = Column(String)
    document_a_path = Column(String)
    document_b_path = Column(String)
    changes = Column(JSON, default=list)
    summary = Column(Text)
    status = Column(String, default="pending")
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class ChatSessionDB(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=generate_id)
    user_id = Column(String, ForeignKey("users.id"))
    title = Column(String)
    context = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ChatMessageDB(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=generate_id)
    session_id = Column(String, ForeignKey("chat_sessions.id"))
    role = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class FavoriteDB(Base):
    __tablename__ = "favorites"

    id = Column(String, primary_key=True, default=generate_id)
    user_id = Column(String, ForeignKey("users.id"))
    item_type = Column(String)
    item_id = Column(String)
    title = Column(String)
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

async def ensure_legacy_schema(conn):
    table_info_result = await conn.execute(text("PRAGMA table_info(comparisons)"))
    comparison_columns = {row[1] for row in table_info_result.fetchall()}

    if "status" not in comparison_columns:
        await conn.execute(text("ALTER TABLE comparisons ADD COLUMN status VARCHAR DEFAULT 'pending'"))

    if "completed_at" not in comparison_columns:
        await conn.execute(text("ALTER TABLE comparisons ADD COLUMN completed_at DATETIME"))

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await ensure_legacy_schema(conn)

async def get_db():
    async with async_session() as session:
        yield session
