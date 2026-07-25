import os
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "法律AI")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # AI API
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_API_URL: str = os.getenv("AI_API_URL", "https://api.deepseek.com/v1/chat/completions")
    AI_MODEL: str = os.getenv("AI_MODEL", "deepseek-v4-flash")

    # 数据库
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR}/legal_ai.db")

    # ChromaDB
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", str(BASE_DIR / "data" / "vector_db"))

    # 上传文件
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads"))
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))

    # OCR
    OCR_PRIMARY_ENGINE: str = os.getenv("OCR_PRIMARY_ENGINE", "paddle").lower()
    OCR_FALLBACK_ENGINE: str = os.getenv("OCR_FALLBACK_ENGINE", "tesseract").lower()
    OCR_ENABLE_GPU: bool = os.getenv("OCR_ENABLE_GPU", "false").lower() == "true"
    OCR_LANG: str = os.getenv("OCR_LANG", "ch")
    OCR_MIN_WIDTH: int = int(os.getenv("OCR_MIN_WIDTH", "2200"))
    OCR_BINARIZE_THRESHOLD: int = int(os.getenv("OCR_BINARIZE_THRESHOLD", "0"))
    OCR_AUTO_CONTRAST_CUTOFF: int = int(os.getenv("OCR_AUTO_CONTRAST_CUTOFF", "2"))
    OCR_SHARPEN_FACTOR: float = float(os.getenv("OCR_SHARPEN_FACTOR", "1.6"))
    OCR_CONTRAST_FACTOR: float = float(os.getenv("OCR_CONTRAST_FACTOR", "1.2"))
    OCR_JOIN_CJK_SPACES: bool = os.getenv("OCR_JOIN_CJK_SPACES", "true").lower() == "true"
    OCR_PADDLE_USE_ANGLE_CLS: bool = os.getenv("OCR_PADDLE_USE_ANGLE_CLS", "true").lower() == "true"
    OCR_PADDLE_DET_LIMIT_SIDE_LEN: int = int(os.getenv("OCR_PADDLE_DET_LIMIT_SIDE_LEN", "1920"))
    OCR_PADDLE_SHOW_LOG: bool = os.getenv("OCR_PADDLE_SHOW_LOG", "false").lower() == "true"
    TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", "")
    TESSERACT_LANG: str = os.getenv("TESSERACT_LANG", "chi_sim+eng")
    TESSERACT_CONFIG: str = os.getenv("TESSERACT_CONFIG", "--oem 1 --psm 6")

    # 法条数据路径
    CRIMINAL_LAW_PATH: str = str(BASE_DIR / "data" / "criminal_law.json")
    CIVIL_LAW_PATH: str = str(BASE_DIR / "data" / "civil_law.json")

    # 鉴权与安全
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me-in-production-please")
    JWT_ALG: str = os.getenv("JWT_ALG", "HS256")
    ACCESS_TOKEN_TTL_MIN: int = int(os.getenv("ACCESS_TOKEN_TTL_MIN", "60"))
    REFRESH_TOKEN_TTL_DAYS: int = int(os.getenv("REFRESH_TOKEN_TTL_DAYS", "14"))
    CORS_ALLOW_ORIGINS: str = os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000,http://127.0.0.1:8000",
    )

    # 默认管理员种子
    DEFAULT_ADMIN_USERNAME: str = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    DEFAULT_ADMIN_PASSWORD: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "Admin@12345")
    DEFAULT_ADMIN_EMAIL: str = os.getenv("DEFAULT_ADMIN_EMAIL", "")
    DEFAULT_ADMIN_NICKNAME: str = os.getenv("DEFAULT_ADMIN_NICKNAME", "系统管理员")

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
