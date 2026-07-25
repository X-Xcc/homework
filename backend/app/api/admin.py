"""管理后台 API：用户管理、统计等。全部走 require_admin 守卫。"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.api.deps import require_admin
from app.core.security import hash_password
from app.models.database import (
    AnalysisDB,
    ChatMessageDB,
    ChatSessionDB,
    ComparisonDB,
    FavoriteDB,
    ROLE_ADMIN,
    ROLE_USER,
    UserDB,
    UserStatus,
    get_db,
)


router = APIRouter(prefix="/api/admin", tags=["admin"])


class AdminUserListItem(BaseModel):
    id: str
    username: Optional[str] = None
    email: Optional[str] = None
    nickname: Optional[str] = None
    role: str
    status: str
    created_at: Optional[str] = None
    last_login_at: Optional[str] = None
    analysis_count: int = 0
    chat_count: int = 0


class AdminUserListResponse(BaseModel):
    items: list[AdminUserListItem]
    total: int
    page: int
    page_size: int


class AdminUserUpdate(BaseModel):
    role: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    nickname: Optional[str] = Field(default=None, max_length=32)
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)


class AdminStats(BaseModel):
    user_total: int
    user_active: int
    user_admin: int
    analysis_total: int
    comparison_total: int
    chat_session_total: int
    favorite_total: int
    recent_24h_signups: int


def _public_admin_user(user: UserDB, analysis_count: int, chat_count: int) -> AdminUserListItem:
    return AdminUserListItem(
        id=user.id,
        username=user.username,
        email=user.email,
        nickname=user.nickname,
        role=user.role or ROLE_USER,
        status=user.status or UserStatus.ACTIVE,
        created_at=user.created_at.isoformat() if user.created_at else None,
        last_login_at=user.last_login_at.isoformat() if user.last_login_at else None,
        analysis_count=analysis_count,
        chat_count=chat_count,
    )


@router.get("/users", response_model=AdminUserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None, description="按 username/email/nickname 模糊匹配"),
    role: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    _admin: UserDB = Depends(require_admin),
):
    base = select(UserDB)
    if keyword:
        like = f"%{keyword.strip()}%"
        base = base.where(
            (UserDB.username.ilike(like))
            | (UserDB.email.ilike(like))
            | (UserDB.nickname.ilike(like))
        )
    if role:
        base = base.where(UserDB.role == role)
    if status_filter:
        base = base.where(UserDB.status == status_filter)

    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
    rows = (
        await db.execute(
            base.order_by(desc(UserDB.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    ).scalars().all()

    user_ids = [u.id for u in rows]
    analysis_counts: dict[str, int] = {}
    chat_counts: dict[str, int] = {}
    if user_ids:
        for uid, count in (await db.execute(
            select(AnalysisDB.user_id, func.count())
            .where(AnalysisDB.user_id.in_(user_ids))
            .group_by(AnalysisDB.user_id)
        )).all():
            analysis_counts[uid] = count
        for uid, count in (await db.execute(
            select(ChatSessionDB.user_id, func.count())
            .where(ChatSessionDB.user_id.in_(user_ids))
            .group_by(ChatSessionDB.user_id)
        )).all():
            chat_counts[uid] = count

    return AdminUserListResponse(
        items=[_public_admin_user(u, analysis_counts.get(u.id, 0), chat_counts.get(u.id, 0)) for u in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.patch("/users/{user_id}", response_model=AdminUserListItem)
async def update_user(
    user_id: str,
    payload: AdminUserUpdate,
    db: AsyncSession = Depends(get_db),
    admin: UserDB = Depends(require_admin),
):
    user = await db.get(UserDB, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    if payload.role is not None:
        if payload.role not in {ROLE_USER, ROLE_ADMIN}:
            raise HTTPException(status_code=400, detail="角色取值不合法")
        # 防止最后一个管理员被降级
        if user.role == ROLE_ADMIN and payload.role != ROLE_ADMIN:
            admin_count = (await db.execute(
                select(func.count()).select_from(UserDB).where(UserDB.role == ROLE_ADMIN)
            )).scalar() or 0
            if admin_count <= 1:
                raise HTTPException(status_code=400, detail="系统至少保留一名管理员")
        user.role = payload.role

    if payload.status is not None:
        if payload.status not in {UserStatus.ACTIVE, UserStatus.DISABLED}:
            raise HTTPException(status_code=400, detail="状态取值不合法")
        if user.id == admin.id and payload.status != UserStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="不能停用当前登录的管理员账号")
        user.status = payload.status

    if payload.nickname is not None:
        user.nickname = payload.nickname

    if payload.password:
        user.password_hash = hash_password(payload.password)

    await db.commit()
    await db.refresh(user)

    analysis_count = (await db.execute(
        select(func.count()).select_from(AnalysisDB).where(AnalysisDB.user_id == user.id)
    )).scalar() or 0
    chat_count = (await db.execute(
        select(func.count()).select_from(ChatSessionDB).where(ChatSessionDB.user_id == user.id)
    )).scalar() or 0
    return _public_admin_user(user, analysis_count, chat_count)


@router.get("/stats", response_model=AdminStats)
async def admin_stats(
    db: AsyncSession = Depends(get_db),
    _admin: UserDB = Depends(require_admin),
):
    user_total = (await db.execute(select(func.count()).select_from(UserDB))).scalar() or 0
    user_active = (await db.execute(
        select(func.count()).select_from(UserDB).where(UserDB.status == UserStatus.ACTIVE)
    )).scalar() or 0
    user_admin = (await db.execute(
        select(func.count()).select_from(UserDB).where(UserDB.role == ROLE_ADMIN)
    )).scalar() or 0
    analysis_total = (await db.execute(select(func.count()).select_from(AnalysisDB))).scalar() or 0
    comparison_total = (await db.execute(select(func.count()).select_from(ComparisonDB))).scalar() or 0
    chat_total = (await db.execute(select(func.count()).select_from(ChatSessionDB))).scalar() or 0
    favorite_total = (await db.execute(select(func.count()).select_from(FavoriteDB))).scalar() or 0

    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    recent_signups = (await db.execute(
        select(func.count()).select_from(UserDB).where(UserDB.created_at >= cutoff)
    )).scalar() or 0

    return AdminStats(
        user_total=user_total,
        user_active=user_active,
        user_admin=user_admin,
        analysis_total=analysis_total,
        comparison_total=comparison_total,
        chat_session_total=chat_total,
        favorite_total=favorite_total,
        recent_24h_signups=recent_signups,
    )



# --- Admin resource listing endpoints ---

@router.get("/analyses")
async def list_analyses(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _admin: UserDB = Depends(require_admin),
):
    rows = (await db.execute(
        select(AnalysisDB).order_by(desc(AnalysisDB.created_at))
        .offset((page - 1) * page_size).limit(page_size)
    )).scalars().all()

    result = []
    for a in rows:
        username = None
        if a.user_id:
            user = await db.get(UserDB, a.user_id)
            if user:
                username = user.username or user.nickname
        result.append({
            "id": a.id,
            "document_name": a.document_name,
            "username": username,
            "status": a.status or "completed",
            "overall_risk_level": (a.risks or {}).get("overall_risk_level") if isinstance(a.risks, dict) else None,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        })
    return result


@router.get("/comparisons")
async def list_comparisons(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _admin: UserDB = Depends(require_admin),
):
    rows = (await db.execute(
        select(ComparisonDB).order_by(desc(ComparisonDB.created_at))
        .offset((page - 1) * page_size).limit(page_size)
    )).scalars().all()

    result = []
    for c in rows:
        username = None
        if c.user_id:
            user = await db.get(UserDB, c.user_id)
            if user:
                username = user.username or user.nickname
        result.append({
            "id": c.id,
            "document_a": c.document_a,
            "document_b": c.document_b,
            "username": username,
            "status": c.status or "completed",
            "changes_count": len(c.changes) if isinstance(c.changes, list) else 0,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        })
    return result


@router.get("/chat-sessions")
async def list_chat_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _admin: UserDB = Depends(require_admin),
):
    rows = (await db.execute(
        select(ChatSessionDB).order_by(desc(ChatSessionDB.updated_at))
        .offset((page - 1) * page_size).limit(page_size)
    )).scalars().all()

    result = []
    for s in rows:
        username = None
        if s.user_id:
            user = await db.get(UserDB, s.user_id)
            if user:
                username = user.username or user.nickname
        msg_count = (await db.execute(
            select(func.count()).select_from(ChatMessageDB).where(ChatMessageDB.session_id == s.id)
        )).scalar() or 0
        result.append({
            "id": s.id,
            "title": s.title or "???",
            "username": username,
            "message_count": msg_count,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
        })
    return result

