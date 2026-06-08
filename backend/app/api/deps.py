from fastapi import Header, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from app.models.database import get_db, UserDB

ANONYMOUS_OPENID_PREFIX = "anon:"
ANONYMOUS_NICKNAME_PREFIX = "匿名法务用户"


def build_anonymous_openid(client_id: str) -> str:
    return f"{ANONYMOUS_OPENID_PREFIX}{client_id}"


async def get_or_create_user_by_client_id(
    client_id: str,
    db: AsyncSession,
    nickname: Optional[str] = None,
):
    openid = build_anonymous_openid(client_id)
    query = select(UserDB).where(UserDB.openid == openid)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        user = UserDB(
            id=str(uuid.uuid4()),
            openid=openid,
            nickname=nickname or f"{ANONYMOUS_NICKNAME_PREFIX}",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


async def get_current_user(
    x_user_id: Optional[str] = Header(default=None),
    x_client_id: Optional[str] = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    if x_user_id:
        user = await db.get(UserDB, x_user_id)
        if user:
            return user

    if not x_client_id:
        raise HTTPException(status_code=400, detail="缺少用户标识")

    return await get_or_create_user_by_client_id(x_client_id, db)
