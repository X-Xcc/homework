from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
import os
import uuid
from datetime import datetime
import json

from app.config import settings
from app.core.document_service import document_parser
from app.core.ai_analyzer import ai_analyzer
from app.models.database import get_db, AnalysisDB, ComparisonDB, UserDB
from app.api.deps import get_current_user
from app.core.rate_limit import ai_rate_limit

router = APIRouter(prefix="/api/document", tags=["document"])


def compute_overall_risk_level(risks):
    if any((risk or {}).get("level") == "high" for risk in risks or []):
        return "high"
    if any((risk or {}).get("level") == "medium" for risk in risks or []):
        return "medium"
    return "low"


def compute_overall_score(risks):
    penalty = 0
    for risk in risks or []:
        level = (risk or {}).get("level")
        if level == "high":
            penalty += 25
        elif level == "medium":
            penalty += 12
        else:
            penalty += 5
    return max(20, 100 - penalty)


@router.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _rate: None = Depends(ai_rate_limit),
    current_user: UserDB = Depends(get_current_user),
):
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{ext}")

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    is_valid, msg = document_parser.validate_file(file_path, settings.MAX_FILE_SIZE)
    if not is_valid:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=msg)

    try:
        text = document_parser.parse(file_path)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"文档解析失败: {str(e)}")

    analysis = AnalysisDB(
        id=file_id,
        user_id=current_user.id,
        document_name=file.filename,
        document_path=file_path,
        status="processing"
    )
    db.add(analysis)
    current_user.analysis_count = (current_user.analysis_count or 0) + 1
    await db.commit()

    try:
        result = await ai_analyzer.analyze_contract(text)

        analysis.status = "completed"
        analysis.risks = result.get("risks", [])
        analysis.summary = result.get("summary", "")
        analysis.completed_at = datetime.utcnow()
        await db.commit()

        overall_risk_level = result.get("overall_risk_level") or compute_overall_risk_level(result.get("risks", []))
        overall_score = result.get("overall_score") if result.get("overall_score") is not None else compute_overall_score(result.get("risks", []))

        return {
            "id": file_id,
            "document_name": file.filename,
            "status": "completed",
            "risks": result.get("risks", []),
            "summary": result.get("summary", ""),
            "overall_risk_level": overall_risk_level,
            "overall_score": overall_score
        }
    except Exception as e:
        analysis.status = "failed"
        await db.commit()
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@router.post("/analyze/stream")
async def analyze_document_stream(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _rate: None = Depends(ai_rate_limit),
    current_user: UserDB = Depends(get_current_user),
):
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{ext}")

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    is_valid, msg = document_parser.validate_file(file_path, settings.MAX_FILE_SIZE)
    if not is_valid:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=msg)

    try:
        text = document_parser.parse(file_path)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"文档解析失败: {str(e)}")

    analysis = AnalysisDB(
        id=file_id,
        user_id=current_user.id,
        document_name=file.filename,
        document_path=file_path,
        status="processing"
    )
    db.add(analysis)
    current_user.analysis_count = (current_user.analysis_count or 0) + 1
    await db.commit()

    async def generate():
        chunks = []
        try:
            async for chunk in ai_analyzer.analyze_contract_stream(text):
                chunks.append(chunk)
                yield f"data: {json.dumps({'content': chunk})}\n\n"

            full_response = ''.join(chunks)
            parsed_result = {}
            try:
                parsed_result = json.loads(full_response)
            except json.JSONDecodeError:
                parsed_result = {
                    "summary": full_response,
                    "risks": []
                }

            risks = parsed_result.get("risks", [])
            analysis.status = "completed"
            analysis.risks = risks
            analysis.summary = parsed_result.get("summary", full_response)
            analysis.completed_at = datetime.utcnow()
            await db.commit()

            overall_risk_level = parsed_result.get("overall_risk_level") or compute_overall_risk_level(risks)
            overall_score = parsed_result.get("overall_score") if parsed_result.get("overall_score") is not None else compute_overall_score(risks)
            yield f"data: {json.dumps({'result': {'id': file_id, 'document_name': file.filename, 'status': 'completed', 'summary': analysis.summary, 'risks': risks, 'overall_risk_level': overall_risk_level, 'overall_score': overall_score}})}\n\n"
        except Exception as e:
            analysis.status = "failed"
            await db.commit()
            yield f"data: {json.dumps({'content': f'错误: {str(e)}'})}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@router.post("/compare")
async def compare_documents(
    file_a: UploadFile = File(...),
    file_b: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _rate: None = Depends(ai_rate_limit),
    current_user: UserDB = Depends(get_current_user),
):
    files = []
    texts = []

    for file in [file_a, file_b]:
        file_id = str(uuid.uuid4())
        ext = os.path.splitext(file.filename)[1]
        file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{ext}")

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        is_valid, msg = document_parser.validate_file(file_path, settings.MAX_FILE_SIZE)
        if not is_valid:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail=msg)

        try:
            text = document_parser.parse(file_path)
            texts.append(text)
            files.append({"id": file_id, "name": file.filename, "path": file_path})
        except Exception as e:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail=f"文档解析失败: {str(e)}")

    comparison_id = str(uuid.uuid4())
    comparison = ComparisonDB(
        id=comparison_id,
        user_id=current_user.id,
        document_a=file_a.filename,
        document_b=file_b.filename,
        document_a_path=files[0]["path"],
        document_b_path=files[1]["path"],
        status="processing"
    )
    db.add(comparison)
    await db.commit()

    try:
        result = await ai_analyzer.compare_documents(texts[0], texts[1])

        comparison.changes = result.get("changes", [])
        comparison.summary = result.get("summary", "")
        comparison.status = "completed"
        comparison.completed_at = datetime.utcnow()
        await db.commit()

        return {
            "id": comparison_id,
            "document_a": file_a.filename,
            "document_b": file_b.filename,
            "changes": result.get("changes", []),
            "summary": result.get("summary", ""),
            "status": "completed"
        }
    except Exception as e:
        comparison.status = "failed"
        await db.commit()
        raise HTTPException(status_code=500, detail=f"比较失败: {str(e)}")

@router.get("/comparisons/{comparison_id}")
async def get_comparison(
    comparison_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    comparison = await db.get(ComparisonDB, comparison_id)
    if not comparison or comparison.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="对比记录未找到")

    return {
        "id": comparison.id,
        "document_a": comparison.document_a,
        "document_b": comparison.document_b,
        "changes": comparison.changes,
        "summary": comparison.summary,
        "status": comparison.status,
        "created_at": comparison.created_at,
        "completed_at": comparison.completed_at
    }


@router.get("/analysis/{analysis_id}")
async def get_analysis(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    analysis = await db.get(AnalysisDB, analysis_id)
    if not analysis or analysis.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="分析记录未找到")

    return {
        "id": analysis.id,
        "document_name": analysis.document_name,
        "status": analysis.status,
        "risks": analysis.risks,
        "summary": analysis.summary,
        "overall_risk_level": "high" if any((risk or {}).get("level") == "high" for risk in (analysis.risks or [])) else "medium" if any((risk or {}).get("level") == "medium" for risk in (analysis.risks or [])) else "low",
        "overall_score": max(20, 100 - sum(25 if (risk or {}).get("level") == "high" else 12 if (risk or {}).get("level") == "medium" else 5 for risk in (analysis.risks or []))),
        "created_at": analysis.created_at,
        "completed_at": analysis.completed_at
    }


from app.api.export_utils import ExportRequest, _generate_txt, _generate_docx, _generate_pdf
import json

@router.post("/export")
async def export_report(
    req: ExportRequest,
    current_user: UserDB = Depends(get_current_user),
):
    fmt = req.format.lower()
    if fmt not in ("txt", "docx", "pdf"):
        raise HTTPException(status_code=400, detail=f"不支持的格式: {fmt}，仅支持 txt/docx/pdf")

    generators = {
        "txt": (_generate_txt, "text/plain; charset=utf-8", ".txt"),
        "docx": (_generate_docx, "application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx"),
        "pdf": (_generate_pdf, "application/pdf", ".pdf"),
    }
    gen_fn, media_type, ext = generators[fmt]
    buf = gen_fn(req)
    from urllib.parse import quote
    raw_filename = f"分析报告_{req.document_name or '未知文档'}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
    safe_filename = quote(raw_filename)
    content_disposition = f"attachment; filename*=UTF-8''{safe_filename}"

    return Response(
        content=buf.getvalue(),
        media_type=media_type,
        headers={"Content-Disposition": content_disposition}
    )


