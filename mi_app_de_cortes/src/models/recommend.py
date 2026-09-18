"""Pydantic models for Feature 002 - Response schemas"""

from pydantic import BaseModel


class Recommendation(BaseModel):
    """Single haircut recommendation."""
    style_id: str
    style_name: str
    description: str
    image_url: bytes


class RecommendResponse(BaseModel):
    """Response for /api/recommend endpoint."""
    success: bool
    recommendations: list[Recommendation]
