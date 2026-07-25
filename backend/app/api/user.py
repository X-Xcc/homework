from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Body, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, or_
from typing import Optional
import re
import uuid

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.database import (
    ROLE_ADMIN,
    ROLE_USER,
    AnalysisDB,
    ChatSessionDB,
    ComparisonDB,
    FavoriteDB,
    UserDB,
    UserStatus,
    get_db,
)
from app.api.deps import get_current_user
from app.core.risk import compute_overall_risk_level, compute_overall_score

bearer_scheme = HTTPBearer(auto_error=False)

USERNAME_RE = re.compile(r"^[A-Za-z0-9_\-.]{3,32}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


router = APIRouter(prefix="/api/user", tags=["user"])


# ---------------------------------------------------------------------------
# 鉴权相关模型
# ---------------------------------------------------------------------------


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=8, max_length=128)
    email: Optional[EmailStr] = None
    nickname: Optional[str] = Field(default=None, max_length=32)


class LoginRequest(BaseModel):
    account: str = Field(min_length=1, max_length=128, description="用户名或邮箱")
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthUserInfo(BaseModel):
    id: str
    username: Optional[str] = None
    email: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    role: str
    status: str
    created_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None


def _validate_username(value: str) -> str:
    if not USERNAME_RE.match(value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名仅支持字母/数字/_-.-，长度 3-32",
        )
    return value


def _validate_password(value: str) -> str:
    if len(value) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码至少 8 位",
        )
    if len(set(value)) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码过于简单，请包含至少 3 种不同字符",
        )
    return value


def _public_user(user: UserDB) -> AuthUserInfo:
    return AuthUserInfo(
        id=user.id,
        username=user.username,
        email=user.email,
        nickname=user.nickname,
        avatar=user.avatar,
        role=user.role or ROLE_USER,
        status=user.status or UserStatus.ACTIVE,
        created_at=user.created_at,
        last_login_at=user.last_login_at,
    )


def _build_token_pair(user: UserDB) -> TokenPair:
    from app.config import settings

    access = create_access_token(user.id, user.role or ROLE_USER)
    refresh = create_refresh_token(user.id, user.role or ROLE_USER)
    return TokenPair(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.ACCESS_TOKEN_TTL_MIN * 60,
    )


# ---------------------------------------------------------------------------
# 鉴权路由
# ---------------------------------------------------------------------------


@router.post("/register", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    username = _validate_username(payload.username)
    _validate_password(payload.password)
    email = (payload.email or "").strip().lower() or None
    if email and not EMAIL_RE.match(email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱格式不正确")

    conditions = [UserDB.username == username]
    if email:
        conditions.append(UserDB.email == email)
    result = await db.execute(select(UserDB).where(or_(*conditions)))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名或邮箱已存在")

    user = UserDB(
        id=str(uuid.uuid4()),
        username=username,
        email=email,
        password_hash=hash_password(payload.password),
        nickname=payload.nickname or username,
        role=ROLE_USER,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return _build_token_pair(user)


@router.post("/login", response_model=TokenPair)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    account = payload.account.strip()
    if not account:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请输入账号")

    if EMAIL_RE.match(account):
        condition = UserDB.email == account.lower()
    else:
        condition = UserDB.username == account

    result = await db.execute(select(UserDB).where(condition))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误",
        )
    if user.status and user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已停用")

    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)
    return _build_token_pair(user)


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        decoded = decode_token(payload.refresh_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="refresh token 无效或已过期",
        )
    if decoded.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌类型错误，请使用 refresh token",
        )
    user = await db.get(UserDB, decoded.get("sub"))
    if not user or (user.status and user.status != UserStatus.ACTIVE):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已停用",
        )
    return _build_token_pair(user)


@router.post("/logout")
async def logout(current_user: UserDB = Depends(get_current_user)):
    # 当前版本为无状态 JWT，前端清除 token 即视为登出；
    # 保留接口用于未来接入黑名单 / 会话表。
    return {"message": "已登出", "user_id": current_user.id}


@router.get("/me", response_model=AuthUserInfo)
async def get_me(current_user: UserDB = Depends(get_current_user)):
    return _public_user(current_user)


@router.get("/me/stats")
async def get_me_stats(
    db: AsyncSession = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    favorite_count = (await db.execute(
        select(func.count()).select_from(FavoriteDB).where(FavoriteDB.user_id == current_user.id)
    )).scalar() or 0
    analysis_count = (await db.execute(
        select(func.count()).select_from(AnalysisDB).where(AnalysisDB.user_id == current_user.id)
    )).scalar() or 0
    comparison_count = (await db.execute(
        select(func.count()).select_from(ComparisonDB).where(ComparisonDB.user_id == current_user.id)
    )).scalar() or 0
    history_count = (await db.execute(
        select(func.count()).select_from(ChatSessionDB).where(ChatSessionDB.user_id == current_user.id)
    )).scalar() or 0

    return {
        "id": current_user.id,
        "analysis_count": analysis_count,
        "chat_count": history_count,
        "favorite_count": favorite_count,
        "comparison_count": comparison_count,
    }


@router.post("/anonymous")
async def create_anonymous_user(
    client_id: str = Body(..., embed=True),
    nickname: Optional[str] = Body(default=None, embed=True),
    db: AsyncSession = Depends(get_db),
):
    """保留匿名入口用于演示/测试，不参与正式业务链路。"""
    openid = f"anon:{client_id}"

    query = select(UserDB).where(UserDB.openid == openid)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        user = UserDB(
            id=str(uuid.uuid4()),
            openid=openid,
            nickname=nickname or f"匿名用户-{client_id[:6]}",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    from app.core.security import create_access_token, create_refresh_token
    from app.config import settings

    access_token = create_access_token(user.id, user.role or "user")
    refresh_token = create_refresh_token(user.id, user.role or "user")

    return {
        "id": user.id,
        "client_id": client_id,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "role": user.role,
        "status": user.status,
        "analysis_count": user.analysis_count,
        "chat_count": user.chat_count,
        "created_at": user.created_at,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_TTL_MIN * 60,
    }


@router.get("/profile/{user_id}")
async def get_profile(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问该用户资料")

    user = await db.get(UserDB, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户未找到")

    return {
        "id": user.id,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "analysis_count": user.analysis_count,
        "chat_count": user.chat_count,
        "created_at": user.created_at
    }


@router.get("/history")
async def get_history(
    limit: int = Query(50, ge=1, le=200),
    item_type: Optional[str] = Query(None, alias="type"),
    db: AsyncSession = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    chat_query = (
        select(ChatSessionDB)
        .where(ChatSessionDB.user_id == current_user.id)
        .order_by(desc(ChatSessionDB.updated_at))
        .limit(limit)
    )
    analysis_query = (
        select(AnalysisDB)
        .where(AnalysisDB.user_id == current_user.id)
        .order_by(desc(AnalysisDB.created_at))
        .limit(limit)
    )
    comparison_query = (
        select(ComparisonDB)
        .where(ComparisonDB.user_id == current_user.id)
        .order_by(desc(ComparisonDB.created_at))
        .limit(limit)
    )

    sessions = (await db.execute(chat_query)).scalars().all()
    analyses = (await db.execute(analysis_query)).scalars().all()
    comparisons = (await db.execute(comparison_query)).scalars().all()

    items = []
    if item_type in (None, "chat"):
        items.extend([
            {
                "id": item.id,
                "type": "chat",
                "title": item.title,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
            }
            for item in sessions
        ])
    if item_type in (None, "analysis"):
        items.extend([
            {
                "id": item.id,
                "type": "analysis",
                "title": item.document_name,
                "status": item.status,
                "created_at": item.created_at,
                "updated_at": item.completed_at or item.created_at,
                "overall_risk_level": compute_overall_risk_level(item.risks or []),
                "overall_score": compute_overall_score(item.risks or []),
            }
            for item in analyses
        ])
    if item_type in (None, "comparison"):
        items.extend([
            {
                "id": item.id,
                "type": "comparison",
                "title": f"{item.document_a} vs {item.document_b}",
                "document_a": item.document_a,
                "document_b": item.document_b,
                "status": item.status,
                "created_at": item.created_at,
                "updated_at": item.completed_at or item.created_at,
            }
            for item in comparisons
        ])

    items.sort(key=lambda x: x.get("updated_at") or x.get("created_at"), reverse=True)
    return items[:limit]


@router.post("/favorites")
async def add_favorite(
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    item_type = payload.get("item_type")
    item_id = payload.get("item_id")
    title = payload.get("title")
    summary = payload.get("summary")

    if not item_type or not item_id:
        raise HTTPException(status_code=400, detail="缺少收藏参数")

    query = select(FavoriteDB).where(
        FavoriteDB.user_id == current_user.id,
        FavoriteDB.item_type == item_type,
        FavoriteDB.item_id == item_id
    )
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="已收藏")

    favorite = FavoriteDB(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        item_type=item_type,
        item_id=item_id,
        title=title,
        summary=summary
    )
    db.add(favorite)
    await db.commit()

    return {"id": favorite.id, "message": "收藏成功", "title": title}


@router.delete("/favorites/{favorite_id}")
async def remove_favorite(
    favorite_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    favorite = await db.get(FavoriteDB, favorite_id)
    if not favorite or favorite.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="收藏未找到")

    await db.delete(favorite)
    await db.commit()

    return {"message": "取消收藏"}


@router.get("/favorites")
async def list_favorites(
    item_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    query = select(FavoriteDB).where(FavoriteDB.user_id == current_user.id).order_by(desc(FavoriteDB.created_at))
    if item_type:
        query = query.where(FavoriteDB.item_type == item_type)

    result = await db.execute(query)
    favorites = result.scalars().all()

    return [{
        "id": f.id,
        "item_type": f.item_type,
        "item_id": f.item_id,
        "title": f.title,
        "summary": f.summary,
        "created_at": f.created_at
    } for f in favorites]


def _build_suggested_actions(
    analysis_count: int,
    comparison_count: int,
    chat_count: int,
    favorite_count: int,
    recent_analyses: list,
    recent_sessions: list,
) -> list[dict]:
    """根据用户当前数据生成引导性操作建议。"""
    actions: list[dict] = []

    if analysis_count == 0:
        actions.append({
            "id": "first-analysis",
            "title": "上传第一份合同",
            "description": "上传合同文档，AI 将自动识别风险条款并给出修改建议。",
            "to": "/contracts/analyze",
            "icon": "file-search",
        })

    if comparison_count == 0 and analysis_count > 0:
        actions.append({
            "id": "try-compare",
            "title": "试试合同对比",
            "description": "上传两份合同，AI 自动识别版本差异。",
            "to": "/contracts/compare",
            "icon": "git-compare",
        })

    if chat_count == 0:
        actions.append({
            "id": "try-chat",
            "title": "开始法律问答",
            "description": "向 AI 法律顾问提问，获取专业解答。",
            "to": "/chat",
            "icon": "message-circle",
        })

    # 如果有高风险分析但没有收藏，提示收藏
    has_high_risk = any(
        compute_overall_risk_level((a.risks if a else []) or []) == "high"
        for a in recent_analyses
    )
    if has_high_risk and favorite_count == 0:
        actions.append({
            "id": "save-findings",
            "title": "收藏重要发现",
            "description": "将高风险条款或法条收藏，方便后续查阅。",
            "to": "/favorites",
            "icon": "bookmark",
        })

    # 如果有最近会话但没有继续，提示继续
    if recent_sessions:
        latest = recent_sessions[0]
        actions.append({
            "id": "continue-chat",
            "title": f"继续: {latest.title or '上次对话'}",
            "description": "回到上次的法律问答会话继续讨论。",
            "to": "/chat",
            "icon": "arrow-right",
        })

    # 如果什么都有了，推荐搜索法条
    if not actions:
        actions.append({
            "id": "search-law",
            "title": "检索相关法条",
            "description": "基于民法典、刑法检索相关法律条文。",
            "to": "/search",
            "icon": "search",
        })

    return actions[:4]

@router.get("/workspace")
async def get_workspace_summary(
    db: AsyncSession = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    analyses_query = (
        select(AnalysisDB)
        .where(AnalysisDB.user_id == current_user.id)
        .order_by(desc(AnalysisDB.created_at))
        .limit(5)
    )
    sessions_query = (
        select(ChatSessionDB)
        .where(ChatSessionDB.user_id == current_user.id)
        .order_by(desc(ChatSessionDB.updated_at))
        .limit(5)
    )
    comparisons_query = (
        select(ComparisonDB)
        .where(ComparisonDB.user_id == current_user.id)
        .order_by(desc(ComparisonDB.created_at))
        .limit(5)
    )
    favorites_query = (
        select(FavoriteDB)
        .where(FavoriteDB.user_id == current_user.id)
        .order_by(desc(FavoriteDB.created_at))
        .limit(10)
    )

    analyses = (await db.execute(analyses_query)).scalars().all()
    sessions = (await db.execute(sessions_query)).scalars().all()
    comparisons = (await db.execute(comparisons_query)).scalars().all()
    favorites = (await db.execute(favorites_query)).scalars().all()

    analysis_count = (await db.execute(select(func.count()).select_from(AnalysisDB).where(AnalysisDB.user_id == current_user.id))).scalar() or 0
    comparison_count = (await db.execute(select(func.count()).select_from(ComparisonDB).where(ComparisonDB.user_id == current_user.id))).scalar() or 0
    chat_count = (await db.execute(select(func.count()).select_from(ChatSessionDB).where(ChatSessionDB.user_id == current_user.id))).scalar() or 0
    favorite_count = (await db.execute(select(func.count()).select_from(FavoriteDB).where(FavoriteDB.user_id == current_user.id))).scalar() or 0

    return {
        "stats": {
            "analysis_count": analysis_count,
            "chat_count": chat_count,
            "comparison_count": comparison_count,
            "favorite_count": favorite_count,
        },
        "recent_analyses": [
            {
                "id": item.id,
                "document_name": item.document_name,
                "status": item.status,
                "summary": item.summary,
                "created_at": item.created_at,
                "completed_at": item.completed_at,
                "overall_risk_level": compute_overall_risk_level(item.risks or []),
                "overall_score": compute_overall_score(item.risks or []),
            }
            for item in analyses
        ],
        "recent_sessions": [
            {
                "id": item.id,
                "title": item.title,
                "updated_at": item.updated_at,
                "created_at": item.created_at,
            }
            for item in sessions
        ],
        "recent_comparisons": [
            {
                "id": item.id,
                "document_a": item.document_a,
                "document_b": item.document_b,
                "summary": item.summary,
                "created_at": item.created_at,
            }
            for item in comparisons
        ],
        "favorites": [
            {
                "id": item.id,
                "item_type": item.item_type,
                "item_id": item.item_id,
                "title": item.title,
                "summary": item.summary,
                "created_at": item.created_at,
            }
            for item in favorites
        ],
        "suggested_actions": _build_suggested_actions(
            analysis_count, comparison_count, chat_count, favorite_count,
            analyses, sessions,
        ),
    }
