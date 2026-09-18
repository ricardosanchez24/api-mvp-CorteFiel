"""Tests for generate_recommendations function - Feature 002"""

from unittest.mock import patch
import pytest

from mi_app_de_cortes.src.services.haircut_service import generate_recommendations
from mi_app_de_cortes.src.models.recommend import Recommendation


class TestGenerateRecommendations:
    """Tests for generate_recommendations function"""

    def test_returns_list_of_recommendation_models(self):
        analysis = {
            "face_shape": "oval",
            "recommended_styles": [
                {"id": "undercut", "reason": "Tus pómulos altos favorecen este corte"},
            ],
        }
        with patch("mi_app_de_cortes.src.services.haircut_service.ReplicateClient") as mock_client:
            mock_client.return_value.generate_image.return_value = b"fake_image"
            result = generate_recommendations(b"image_data", analysis)
            assert isinstance(result, list)
            assert all(isinstance(rec, Recommendation) for rec in result)

    def test_uses_ai_recommendations(self):
        analysis = {
            "face_shape": "oval",
            "recommended_styles": [
                {"id": "undercut", "reason": "Tus pómulos altos favorecen este corte"},
                {"id": "fade", "reason": "Tu mandíbula cuadrada se ve bien con transición"},
            ],
        }
        with patch("mi_app_de_cortes.src.services.haircut_service.ReplicateClient") as mock_client:
            mock_client.return_value.generate_image.return_value = b"fake_image"
            result = generate_recommendations(b"image_data", analysis)
            style_ids = [rec.style_id for rec in result]
            assert "undercut" in style_ids
            assert "fade" in style_ids

    def test_each_recommendation_has_reason(self):
        analysis = {
            "face_shape": "oval",
            "recommended_styles": [
                {"id": "undercut", "reason": "Tus pómulos altos favorecen este corte"},
            ],
        }
        with patch("mi_app_de_cortes.src.services.haircut_service.ReplicateClient") as mock_client:
            mock_client.return_value.generate_image.return_value = b"fake_image"
            result = generate_recommendations(b"image_data", analysis)
            for rec in result:
                assert hasattr(rec, "reason")
                assert len(rec.reason) > 0

    def test_calls_replicate_api_for_each_recommendation(self):
        analysis = {
            "face_shape": "oval",
            "recommended_styles": [
                {"id": "undercut", "reason": "Razón 1"},
                {"id": "fade", "reason": "Razón 2"},
                {"id": "textured-crop", "reason": "Razón 3"},
            ],
        }
        with patch("mi_app_de_cortes.src.services.haircut_service.ReplicateClient") as mock_client:
            mock_client.return_value.generate_image.return_value = b"fake_image"
            result = generate_recommendations(b"image_data", analysis)
            assert mock_client.return_value.generate_image.call_count == 3

    def test_returns_empty_when_no_recommendations(self):
        analysis = {
            "face_shape": "oval",
            "recommended_styles": [],
        }
        with patch("mi_app_de_cortes.src.services.haircut_service.ReplicateClient") as mock_client:
            mock_client.return_value.generate_image.return_value = b"fake_image"
            result = generate_recommendations(b"image_data", analysis)
            assert len(result) == 0
