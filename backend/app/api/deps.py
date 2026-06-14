"""鉴权与权限依赖。

鉴权策略：
- 优先解析 `Authorization: Bearer <access_token>`；
- 同时为兼容旧版管理端调试，临时保留 `X-Admin-Token` 等同于 Bearer token 头；
- 不再接受 `X-User-Id` / `X-Client-Id` 伪造身份。
- 角色边界：`require_admin` 用于 `/admin` 相关接口。
"""
from __future__ import annotations

from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import decode_token
from app.models.database import ROLE_ADMIN, ROLE_USER, UserDB, get_db


bearer_scheme = HTTPBearer(auto_error=False)


def _extract_bearer(
    authorization: Optional[str],
    credentials: Optional[HTTPAuthorizationCredentials],
    x_admin_token: Optional[str],
) -> Optional[str]:
    if credentials and credentials.scheme.lower() == "bearer" and credentials.credentials:
        return credentials.credentials
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1].strip() or None
    if x_admin_token:
        return x_admin_token
    return None


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    authorization: Optional[str] = Header(default=None),
    x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token"),
) -> UserDB:
    token = _extract_bearer(authorization, credentials, x_admin_token)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供有效的访问令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="访问令牌无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌类型错误，请使用 access token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌缺少用户标识",
        )

    user = await db.get(UserDB, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")

    if user.status and user.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已停用")

    return user


async def get_optional_user(
    db: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    authorization: Optional[str] = Header(default=None),
) -> Optional[UserDB]:
    token = _extract_bearer(authorization, credentials, None)
    if not token:
        return None
    try:
        payload = decode_token(token)
    except JWTError:
        return None
    if payload.get("type") != "access":
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    return await db.get(UserDB, user_id)


async def require_admin(
    current_user: UserDB = Depends(get_current_user),
) -> UserDB:
    if current_user.role != ROLE_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    return current_user


__all__ = [
    "ROLE_USER",
    "ROLE_ADMIN",
    "get_current_user",
    "get_optional_user",
    "require_admin",
]
