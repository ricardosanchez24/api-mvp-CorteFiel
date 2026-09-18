"""Tests for generate_recommendations function - Feature 002"""

from unittest.mock import patch
import pytest

from mi_app_de_cortes.src.services.haircut_service import generate_recommendations
from mi_app_de_cortes.src.models.recommend import Recommendation


class TestGenerateRecommendations:
    """Tests for generate_recommendations function"""

    def test_returns_list_of_recommendation_models(self):
        with patch("mi_app_de_cortes.src.services.haircut_service.ReplicateClient") as mock_client:
            mock_client.return_value.generate_image.return_value = b"fake_image"
            result = generate_recommendations(b"image_data", {"face_shape": "oval"})
            assert isinstance(result, list)
            assert all(isinstance(rec, Recommendation) for rec in result)

    def test_returns_max_3_recommendations(self):
        with patch("mi_app_de_cortes.src.services.haircut_service.ReplicateClient") as mock_client:
            mock_client.return_value.generate_image.return_value = b"fake_image"
            result = generate_recommendations(b"image_data", {"face_shape": "oval"})
            assert len(result) <= 3

    def test_each_recommendation_has_required_fields(self):
        with patch("mi_app_de_cortes.src.services.haircut_service.ReplicateClient") as mock_client:
            mock_client.return_value.generate_image.return_value = b"fake_image"
            result = generate_recommendations(b"image_data", {"face_shape": "oval"})
            for rec in result:
                assert hasattr(rec, "style_id")
                assert hasattr(rec, "style_name")
                assert hasattr(rec, "description")
                assert hasattr(rec, "image_url")

    def test_filters_by_face_shape(self):
        with patch("mi_app_de_cortes.src.services.haircut_service.ReplicateClient") as mock_client:
            mock_client.return_value.generate_image.return_value = b"fake_image"
            result = generate_recommendations(b"image_data", {"face_shape": "heart"})
            style_ids = [rec.style_id for rec in result]
            assert "undercut" in style_ids

    def test_calls_replicate_api_for_each_style(self):
        with patch("mi_app_de_cortes.src.services.haircut_service.ReplicateClient") as mock_client:
            mock_client.return_value.generate_image.return_value = b"fake_image"
            result = generate_recommendations(b"image_data", {"face_shape": "oval"})
            assert mock_client.return_value.generate_image.call_count == len(result)
