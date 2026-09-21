"""Pydantic models for Feature 002 - schemas de respuesta y de jobs asíncronos."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel


class JobStatus(str, Enum):
    """Estados de un job de recomendación asíncrono."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Recommendation(BaseModel):
    """Una recomendación de corte. image_base64 se renombra en la Fase D."""
    style_id: str
    style_name: str
    description: str
    reason: str
    image_url: bytes


class RecommendResponse(BaseModel):
    """Respuesta de /api/recommend (compatibilidad temporal hasta Fase D)."""
    success: bool
    recommendations: list[Recommendation]


class JobCreateResponse(BaseModel):
    """Respuesta 202 de POST /api/recommend (job encolado)."""
    job_id: str
    status: JobStatus
    status_url: str


class JobStatusResponse(BaseModel):
    """Respuesta de GET /api/recommend/{job_id} (polling)."""
    job_id: str
    status: JobStatus
    error: Optional[str] = None
    recommendations: Optional[list[Recommendation]] = None