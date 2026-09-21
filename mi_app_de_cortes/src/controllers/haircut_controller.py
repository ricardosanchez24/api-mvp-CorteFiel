import json

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from mi_app_de_cortes.src.models.recommend import (
    JobCreateResponse,
    JobStatus,
    JobStatusResponse,
)
from mi_app_de_cortes.src.services import haircut_service
from mi_app_de_cortes.src.services.recommend_job import job_store, schedule_job

router = APIRouter()


@router.post("/analyze")
async def analyze_photo(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        haircut_service.validate_image(image_bytes, file.content_type)
        analysis = haircut_service.analyze_face(image_bytes, file.content_type)
        return {"success": True, "analysis": analysis}
    except ValueError as e:
        status_code = 413 if "10MB" in str(e) else 400
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")


def _parse_analysis(raw: str) -> dict:
    """Parsea y valida el analysis obtenido de /api/analyze (Feature 001)."""
    try:
        analysis = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("analysis must be a valid JSON object") from exc
    if not isinstance(analysis, dict):
        raise ValueError("analysis must be a JSON object")
    if "face_shape" not in analysis:
        raise ValueError("analysis must contain 'face_shape' (from /api/analyze)")
    return analysis


@router.post("/recommend", response_model=JobCreateResponse, status_code=202)
async def recommend_haircut(
    file: UploadFile = File(...),
    analysis: str = Form(...),
):
    """Encola un job asíncrono: recibe la foto + el analysis de /api/analyze.

    Esta feature NO re-analiza la foto (ahorra una llamada Gemini por request).
    Respuesta inmediata 202 con job_id; el resultado se consulta por polling.
    """
    try:
        image_bytes = await file.read()
        haircut_service.validate_image(image_bytes, file.content_type)
        analysis_data = _parse_analysis(analysis)
    except ValueError as e:
        status_code = 413 if "10MB" in str(e) else 400
        raise HTTPException(status_code=status_code, detail=str(e))

    job = job_store.create_job()
    schedule_job(job["job_id"], image_bytes, analysis_data)
    return JobCreateResponse(
        job_id=job["job_id"],
        status=JobStatus.PENDING,
        status_url=f"/api/recommend/{job['job_id']}",
    )


@router.get("/recommend/{job_id}", response_model=JobStatusResponse)
async def get_recommend_job(job_id: str):
    """Consulta el estado de un job y su resultado cuando termina (polling)."""
    job = job_store.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(
        job_id=job["job_id"],
        status=job["status"],
        error=job["error"],
        recommendations=job["recommendations"],
    )