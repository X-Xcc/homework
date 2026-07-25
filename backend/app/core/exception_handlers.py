"""Unified exception handlers for consistent API error responses."""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTPException with consistent response format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "code": exc.status_code,
            "detail": exc.detail,
            "path": str(request.url.path),
        },
        headers=getattr(exc, "headers", None) or {},
    )


async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "code": 422,
            "detail": "请求参数校验失败",
            "errors": errors,
            "path": str(request.url.path),
        },
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle database errors without leaking internals."""
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "code": 500,
            "detail": "数据库操作异常",
            "path": str(request.url.path),
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unexpected errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "code": 500,
            "detail": "服务器内部错误",
            "path": str(request.url.path),
        },
    )
