"""测试夹具：异步 DB / ASGI client / 测试用户。

策略：
- 启动时 monkeypatch `settings.DATABASE_URL` 指向临时 SQLite（`./.tmp_test.db`）
- 每次会话用 `Base.metadata.create_all` 建表，会话结束删表文件
- 跳过默认 admin 自动 seed（避免污染测试库）
- `get_settings` / `get_db` 已经被 FastAPI Depends 解析，无需手动注入
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import AsyncGenerator
import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.security import hash_password
from app.models.database import (
    ROLE_ADMIN,
    ROLE_USER,
    Base,
    UserDB,
    UserStatus,
    get_db,
)


@pytest.fixture(scope="session", autouse=True)
def _patch_database_url():
    """强制测试走临时 SQLite，且禁用 admin 自动 seed。"""
    tmp_dir = tempfile.mkdtemp(prefix="legal-ai-test-")
    db_path = Path(tmp_dir) / "test.db"
    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"
    os.environ["DISABLE_DEFAULT_ADMIN_SEED"] = "1"
    yield
    try:
        db_path.unlink(missing_ok=True)
    except Exception:
        pass


@pytest_asyncio.fixture
async def db_engine():
    """每个测试函数独立的 in-memory 引擎。"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def normal_user(db_session: AsyncSession) -> UserDB:
    user = UserDB(
        id=str(uuid.uuid4()),
        username="alice",
        email="alice@example.com",
        password_hash=hash_password("Strong-Pass-1"),
        nickname="Alice",
        role=ROLE_USER,
        status=UserStatus.ACTIVE,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> UserDB:
    admin = UserDB(
        id=str(uuid.uuid4()),
        username="boss",
        email="boss@example.com",
        password_hash=hash_password("Strong-Pass-1"),
        nickname="Boss",
        role=ROLE_ADMIN,
        status=UserStatus.ACTIVE,
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """构造一个绑定到当前 db_session 的 ASGI 测试客户端。"""
    from app.main import app

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
    app.dependency_overrides.clear()


def auth_header(user: UserDB) -> dict[str, str]:
    """为 httpx 构造 Bearer 头。"""
    from app.core.security import create_access_token
    token = create_access_token(user.id, user.role)
    return {"Authorization": f"Bearer {token}"}
