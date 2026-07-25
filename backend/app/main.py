import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api import chat_router, document_router, search_router, user_router
from app.api.admin import router as admin_router
from app.api.template import router as template_router
from app.config import settings
from app.core.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler,
)
from app.core.rate_limit import rate_limit_middleware
from app.models.database import init_db

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("legal_ai")

FRONTEND_DIST_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not settings.JWT_SECRET or settings.JWT_SECRET == "change-me-in-production-please":
        if not settings.DEBUG:
            raise RuntimeError("生产环境必须设置 JWT_SECRET 环境变量")
    logger.info("Initializing database...")
    await init_db()
    logger.info("Application started")
    yield
    from app.core.ai_analyzer import ai_analyzer
    await ai_analyzer.close()
    logger.info("Application shut down")


app = FastAPI(
    title=settings.APP_NAME,
    description="智能法律顾问系统",
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "search", "description": "法条搜索与相似法条检索"},
        {"name": "document", "description": "文档上传、AI 分析与对比"},
        {"name": "chat", "description": "AI 智能问答与会话管理"},
        {"name": "user", "description": "用户注册、登录、工作台与收藏"},
        {"name": "templates", "description": "合同模板库浏览与详情"},
        {"name": "admin", "description": "管理后台（用户/分析/会话/日志/设置）"},
        {"name": "system", "description": "系统健康检查"},
    ],
)

# ---- Middleware (order matters: last added = first executed) ----

# CORS
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

# Request logging
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = int((time.time() - start) * 1000)
    client = request.client.host if request.client else "unknown"
    logger.info("%s %s %s %d %dms", client, request.method, request.url.path, response.status_code, elapsed)
    return response

# Rate limiting
app.middleware("http")(rate_limit_middleware)


# ---- Exception Handlers ----
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


# ---- API Routes ----
app.include_router(search_router)
app.include_router(document_router)
app.include_router(chat_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(template_router)


@app.get("/health", tags=["system"])
async def health():
    """健康检查：返回 db / ai / ocr / chromadb 子系统状态。"""
    from app.models.database import async_session

    db_ok = False
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    chroma_ok = False
    try:
        from app.core.vector_store import vector_store
        chroma_ok = vector_store.collection is not None
    except Exception:
        chroma_ok = False

    ai_ok = bool(settings.AI_API_KEY)
    ocr_ok = bool(settings.OCR_PRIMARY_ENGINE or settings.OCR_FALLBACK_ENGINE)

    components_ok = all([db_ok, ai_ok, ocr_ok])
    overall = "ok" if components_ok else "degraded"

    payload = {
        "status": overall,
        "components": {
            "db": "ok" if db_ok else "down",
            "ai": "ok" if ai_ok else "missing_api_key",
            "ocr": "ok" if ocr_ok else "not_configured",
            "chromadb": "ok" if chroma_ok else "unavailable",
        },
        "version": app.version,
    }
    code = 200 if overall == "ok" else 503
    return JSONResponse(payload, status_code=code)


# ---- Frontend SPA ----
if FRONTEND_DIST_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST_DIR / "assets")), name="static-assets")

    @app.get("/{full_path:path}", tags=["system"])
    async def serve_spa(full_path: str):
        file_path = FRONTEND_DIST_DIR / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(FRONTEND_DIST_DIR / "index.html"))
