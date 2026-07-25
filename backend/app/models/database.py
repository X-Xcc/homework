from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON, Boolean
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

class UserRole(str):
    USER = "user"
    ADMIN = "admin"

ROLE_USER = "user"
ROLE_ADMIN = "admin"

class UserStatus:
    ACTIVE = "active"
    DISABLED = "disabled"


class UserDB(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_id)
    openid = Column(String, unique=True, index=True, nullable=True)
    username = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=True)
    nickname = Column(String)
    avatar = Column(String)
    phone = Column(String)
    role = Column(String, default=ROLE_USER, nullable=False)
    status = Column(String, default=UserStatus.ACTIVE, nullable=False)
    analysis_count = Column(Integer, default=0)
    chat_count = Column(Integer, default=0)
    last_login_at = Column(DateTime)
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

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_default_admin()


async def seed_default_admin() -> None:
    from app.core.security import hash_password  # local import to avoid cycle
    from sqlalchemy import select

    admin_username = settings.DEFAULT_ADMIN_USERNAME
    admin_password = settings.DEFAULT_ADMIN_PASSWORD
    if not admin_username or not admin_password:
        return

    async with async_session() as session:
        result = await session.execute(
            select(UserDB).where(UserDB.username == admin_username)
        )
        existing = result.scalar_one_or_none()
        if existing:
            return

        admin = UserDB(
            id=str(uuid.uuid4()),
            username=admin_username,
            email=settings.DEFAULT_ADMIN_EMAIL or None,
            password_hash=hash_password(admin_password),
            nickname=settings.DEFAULT_ADMIN_NICKNAME or "系统管理员",
            role=ROLE_ADMIN,
            status=UserStatus.ACTIVE,
        )
        session.add(admin)
        await session.commit()

async def get_db():
    async with async_session() as session:
        yield session
