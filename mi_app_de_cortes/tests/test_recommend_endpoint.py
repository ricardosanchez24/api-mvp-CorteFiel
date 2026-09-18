"""Tests for POST /api/recommend endpoint - Feature 002"""

import io
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from mi_app_de_cortes.app import app
from mi_app_de_cortes.src.models.recommend import Recommendation

client = TestClient(app)


def _make_recommendation(style_id: str, style_name: str, reason: str = "Test reason") -> Recommendation:
    """Helper to create mock Recommendation objects."""
    return Recommendation(
        style_id=style_id,
        style_name=style_name,
        description="Test",
        reason=reason,
        image_url=b"fake",
    )


class TestRecommendEndpoint:
    """Tests for POST /api/recommend"""

    def test_returns_200(self):
        with patch("mi_app_de_cortes.src.controllers.haircut_controller.haircut_service") as mock_service:
            mock_service.validate_image.return_value = None
            mock_service.analyze_face.return_value = {"face_shape": "oval"}
            mock_service.generate_recommendations.return_value = [
                _make_recommendation("undercut", "Undercut"),
            ]
            response = client.post(
                "/api/recommend",
                files={"file": ("test.jpg", io.BytesIO(b"fake_image"), "image/jpeg")},
            )
            assert response.status_code == 200

    def test_returns_recommendations_list(self):
        with patch("mi_app_de_cortes.src.controllers.haircut_controller.haircut_service") as mock_service:
            mock_service.validate_image.return_value = None
            mock_service.analyze_face.return_value = {"face_shape": "oval"}
            mock_service.generate_recommendations.return_value = [
                _make_recommendation("undercut", "Undercut"),
            ]
            response = client.post(
                "/api/recommend",
                files={"file": ("test.jpg", io.BytesIO(b"fake_image"), "image/jpeg")},
            )
            data = response.json()
            assert "recommendations" in data

    def test_returns_3_recommendations(self):
        with patch("mi_app_de_cortes.src.controllers.haircut_controller.haircut_service") as mock_service:
            mock_service.validate_image.return_value = None
            mock_service.analyze_face.return_value = {"face_shape": "oval"}
            mock_service.generate_recommendations.return_value = [
                _make_recommendation("undercut", "Undercut"),
                _make_recommendation("fade", "Fade"),
                _make_recommendation("textured-crop", "Textured Crop"),
            ]
            response = client.post(
                "/api/recommend",
                files={"file": ("test.jpg", io.BytesIO(b"fake_image"), "image/jpeg")},
            )
            data = response.json()
            assert len(data["recommendations"]) == 3

    def test_returns_400_when_no_file(self):
        response = client.post("/api/recommend")
        assert response.status_code == 422

    def test_returns_400_when_invalid_format(self):
        with patch("mi_app_de_cortes.src.controllers.haircut_controller.haircut_service") as mock_service:
            mock_service.validate_image.side_effect = ValueError("Invalid format")
            response = client.post(
                "/api/recommend",
                files={"file": ("test.txt", io.BytesIO(b"fake"), "text/plain")},
            )
            assert response.status_code == 400
