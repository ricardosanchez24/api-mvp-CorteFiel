"""Tests for generate_recommendations function - Feature 002"""

import os
from unittest.mock import MagicMock, patch
import pytest

from mi_app_de_cortes.src.services.haircut_service import generate_recommendations


class TestGenerateRecommendations:
    """Tests for generate_recommendations function"""

    def test_returns_list(self):
        with patch("mi_app_de_cortes.src.services.haircut_service.ReplicateClient") as mock_client:
            mock_client.return_value.generate_image.return_value = b"fake_image"
            result = generate_recommendations(b"image_data", {"face_shape": "oval"})
            assert isinstance(result, list)

    def test_returns_3_recommendations(self):
        with patch("mi_app_de_cortes.src.services.haircut_service.ReplicateClient") as mock_client:
            mock_client.return_value.generate_image.return_value = b"fake_image"
            result = generate_recommendations(b"image_data", {"face_shape": "oval"})
            assert len(result) == 3

    def test_each_recommendation_has_required_fields(self):
        with patch("mi_app_de_cortes.src.services.haircut_service.ReplicateClient") as mock_client:
            mock_client.return_value.generate_image.return_value = b"fake_image"
            result = generate_recommendations(b"image_data", {"face_shape": "oval"})
            for rec in result:
                assert "style_id" in rec
                assert "style_name" in rec
                assert "description" in rec
                assert "image_url" in rec

    def test_calls_replicate_api_for_each_style(self):
        with patch("mi_app_de_cortes.src.services.haircut_service.ReplicateClient") as mock_client:
            mock_client.return_value.generate_image.return_value = b"fake_image"
            generate_recommendations(b"image_data", {"face_shape": "oval"})
            assert mock_client.return_value.generate_image.call_count == 3
