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
    """Una recomendación de corte con la foto del usuario editada (base64 inline)."""
    style_id: str
    style_name: str
    description: str
    reason: str
    image_base64: str


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