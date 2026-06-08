from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from datetime import datetime
import uuid
import json

from app.core.ai_analyzer import ai_analyzer
from app.models.database import get_db, ChatSessionDB, ChatMessageDB, UserDB
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/sessions")
async def create_session(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    try:
        body = await request.json()
    except:
        body = {}

    session_id = str(uuid.uuid4())
    session = ChatSessionDB(
        id=session_id,
        user_id=current_user.id,
        title=body.get("title", "新对话"),
        context=body.get("context")
    )
    db.add(session)
    current_user.chat_count = (current_user.chat_count or 0) + 1
    await db.commit()

    return {
        "id": session_id,
        "title": session.title,
        "created_at": str(session.created_at)
    }

@router.get("/sessions")
async def list_sessions(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    query = (
        select(ChatSessionDB)
        .where(ChatSessionDB.user_id == current_user.id)
        .order_by(desc(ChatSessionDB.updated_at))
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(query)
    sessions = result.scalars().all()

    return [{
        "id": s.id,
        "title": s.title,
        "created_at": str(s.created_at),
        "updated_at": str(s.updated_at)
    } for s in sessions]

@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    session = await db.get(ChatSessionDB, session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="会话未找到")

    query = select(ChatMessageDB).where(ChatMessageDB.session_id == session_id).order_by(ChatMessageDB.created_at)
    result = await db.execute(query)
    messages = result.scalars().all()

    return {
        "id": session.id,
        "title": session.title,
        "context": session.context,
        "created_at": str(session.created_at),
        "messages": [{
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "created_at": str(m.created_at)
        } for m in messages]
    }

@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    session = await db.get(ChatSessionDB, session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="会话未找到")

    try:
        body = await request.json()
    except:
        body = {}

    role = body.get("role", "user")
    content = body.get("content", "")

    user_msg = ChatMessageDB(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role=role,
        content=content
    )
    db.add(user_msg)
    await db.commit()

    query = select(ChatMessageDB).where(ChatMessageDB.session_id == session_id).order_by(ChatMessageDB.created_at)
    result = await db.execute(query)
    history = result.scalars().all()

    messages = [{"role": m.role, "content": m.content} for m in history]

    try:
        ai_response = await ai_analyzer.chat(content, history=messages[:-1], context=session.context)
    except Exception as e:
        ai_response = f"抱歉，AI服务暂时不可用: {str(e)}"

    ai_msg = ChatMessageDB(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role="assistant",
        content=ai_response
    )
    db.add(ai_msg)

    session.updated_at = datetime.utcnow()
    await db.commit()

    return {
        "id": ai_msg.id,
        "role": "assistant",
        "content": ai_response,
        "created_at": str(ai_msg.created_at)
    }

@router.post("/sessions/{session_id}/messages/stream")
async def send_message_stream(
    session_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    session = await db.get(ChatSessionDB, session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="会话未找到")

    try:
        body = await request.json()
    except:
        body = {}

    role = body.get("role", "user")
    content = body.get("content", "")

    user_msg = ChatMessageDB(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role=role,
        content=content
    )
    db.add(user_msg)
    await db.commit()

    query = select(ChatMessageDB).where(ChatMessageDB.session_id == session_id).order_by(ChatMessageDB.created_at)
    result = await db.execute(query)
    history = result.scalars().all()

    messages = [{"role": m.role, "content": m.content} for m in history]

    async def generate():
        full_response = ""
        try:
            async for chunk in ai_analyzer.chat_stream(content, history=messages[:-1], context=session.context):
                full_response += chunk
                yield f"data: {json.dumps({'content': chunk})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'content': f'错误: {str(e)}'})}\n\n"

        if full_response:
            ai_msg = ChatMessageDB(
                id=str(uuid.uuid4()),
                session_id=session_id,
                role="assistant",
                content=full_response
            )
            db.add(ai_msg)
            session.updated_at = datetime.utcnow()
            await db.commit()

        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    session = await db.get(ChatSessionDB, session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="会话未找到")

    await db.delete(session)
    await db.commit()

    return {"message": "会话已删除"}
