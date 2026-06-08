import os
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "法律AI")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # MiMo API
    MIMO_API_KEY: str = os.getenv("MIMO_API_KEY", "")
    MIMO_API_URL: str = os.getenv("MIMO_API_URL", "https://token-plan-cn.xiaomimimo.com/v1/chat/completions")
    MIMO_MODEL: str = os.getenv("MIMO_MODEL", "mimo-v2.5-pro")

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

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
