from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.api import chat_router, document_router, search_router, user_router
from app.api.admin import router as admin_router
from app.api.template import router as template_router
from app.config import settings
from app.models.database import init_db

FRONTEND_DIST_DIR = Path(__file__).resolve().parent.parent.parent / 'frontend' / 'dist'


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not settings.JWT_SECRET or settings.JWT_SECRET == "change-me-in-production-please":
        if not settings.DEBUG:
            raise RuntimeError("生产环境必须设置 JWT_SECRET 环境变量")
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description='智能法律顾问系统',
    version='1.0.0',
    lifespan=lifespan,
)

# CORS 收口：使用白名单，逗号分隔；credentials=True 时不能用通配
allow_origins = [origin.strip() for origin in settings.CORS_ALLOW_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Admin-Token"],
    expose_headers=["Content-Disposition"],
    max_age=600,
)

app.include_router(search_router)
app.include_router(document_router)
app.include_router(chat_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(template_router)


@app.get('/health')
async def health():
    """健康检查：返回 db / ai / ocr 子系统状态。"""
    from app.models.database import async_session
    db_ok = False
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    ai_ok = bool(settings.MIMO_API_KEY)
    ocr_ok = bool(settings.OCR_PRIMARY_ENGINE or settings.OCR_FALLBACK_ENGINE)

    overall = "ok" if db_ok else "degraded"
    payload = {
        "status": overall,
        "components": {
            "db": "ok" if db_ok else "down",
            "ai": "ok" if ai_ok else "missing_api_key",
            "ocr": "ok" if ocr_ok else "not_configured",
        },
        "version": app.version,
    }
    code = 200 if overall == "ok" else 503
    return JSONResponse(payload, status_code=code)


if FRONTEND_DIST_DIR.exists():
    app.mount('/', StaticFiles(directory=str(FRONTEND_DIST_DIR), html=True), name='frontend')
