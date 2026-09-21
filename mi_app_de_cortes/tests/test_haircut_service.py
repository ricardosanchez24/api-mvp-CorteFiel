"""Tests for generate_recommendations - Feature 002 (nueva orquestación).

Flujo: filtrar catálogo por el análisis → la IA elige 3 estilos → Replicate
edita la foto por estilo → base64 inline.
"""

import base64
from contextlib import contextmanager
from unittest.mock import patch

import pytest

from mi_app_de_cortes.src.models.recommend import Recommendation
from mi_app_de_cortes.src.services.haircut_service import generate_recommendations

# Análisis como lo devolvería Feature 001 (la orquestación ya no usa recommended_styles).
VALID_ANALYSIS = {
    "face_shape": "oval",
    "hair_type": "straight",
    "hair_texture": "medium",
    "features": ["jawline"],
    "confidence": "high",
}

SELECTED = [
    {"id": "fade", "reason": "Razón 1"},
    {"id": "undercut", "reason": "Razón 2"},
    {"id": "textured-crop", "reason": "Razón 3"},
]

_SELECT_PATH = "mi_app_de_cortes.src.services.haircut_service.ai_client.select_styles"
_REPLICATE_PATH = (
    "mi_app_de_cortes.src.services.haircut_service.ReplicateClient"
)


def _patch_pipeline(selection=SELECTED, edited_bytes=b"edited_image"):
    """Mockea la elección de la IA y la edición de Replicate (sin llamadas reales).

    Context manager que apila ambos patches y cede (mock_select, mock_gen).
    """
    @contextmanager
    def _stack():
        with patch(_SELECT_PATH, return_value=selection) as mock_select, patch(
            f"{_REPLICATE_PATH}.generate_image", return_value=edited_bytes
        ) as mock_gen:
            yield mock_select, mock_gen
    return _stack()


class TestGenerateRecommendations:
    """Tests de la orquestación con selección mockeada."""

    def test_returns_3_recommendation_models(self):
        with _patch_pipeline() as (mock_select, mock_gen):
            result = generate_recommendations(b"image", VALID_ANALYSIS)
            assert len(result) == 3
            assert all(isinstance(rec, Recommendation) for rec in result)
            mock_select.assert_called_once()
            assert mock_gen.call_count == 3

    def test_uses_ai_selected_styles_in_order(self):
        with _patch_pipeline():
            result = generate_recommendations(b"image", VALID_ANALYSIS)
            assert [rec.style_id for rec in result] == ["fade", "undercut", "textured-crop"]

    def test_each_recommendation_has_reason_from_ai(self):
        with _patch_pipeline():
            result = generate_recommendations(b"image", VALID_ANALYSIS)
            for i, rec in enumerate(result):
                assert rec.reason == SELECTED[i]["reason"]
                assert rec.style_name  # nombre tomado del catálogo

    def test_calls_replicate_once_per_style(self):
        with _patch_pipeline() as (_, mock_gen):
            generate_recommendations(b"image", VALID_ANALYSIS)
            assert mock_gen.call_count == 3

    def test_images_are_valid_base64_of_edited_bytes(self):
        with _patch_pipeline(edited_bytes=b"edited_image"):
            result = generate_recommendations(b"image", VALID_ANALYSIS)
            for rec in result:
                assert base64.b64decode(rec.image_base64) == b"edited_image"

    def test_select_styles_receives_candidates_from_catalog(self):
        """La IA solo recibe estilos compatibles con el análisis (sin skin_tone)."""
        with _patch_pipeline() as (mock_select, _):
            generate_recommendations(b"image", VALID_ANALYSIS)
            args, kwargs = mock_select.call_args
            candidates = args[0]  # primer argumento posicional: la lista del catálogo
            assert candidates  # lista no vacía de estilos compatibles
            for style in candidates:
                assert "oval" in style["face_shapes"]
                assert "straight" in style["hair_types"]
            assert "skin_tone" not in kwargs

    def test_raises_when_ai_returns_wrong_count(self):
        with _patch_pipeline([{"id": "fade", "reason": "Solo uno"}]):
            with pytest.raises(ValueError):
                generate_recommendations(b"image", VALID_ANALYSIS)

    def test_raises_when_ai_returns_duplicate_ids(self):
        selection = [{"id": "fade", "reason": "a"}, {"id": "fade", "reason": "b"},
                     {"id": "undercut", "reason": "c"}]
        with _patch_pipeline(selection):
            with pytest.raises(ValueError):
                generate_recommendations(b"image", VALID_ANALYSIS)

    def test_raises_when_ai_returns_unknown_id(self):
        selection = [{"id": "fade", "reason": "a"}, {"id": "under cut", "reason": "b"},
                     {"id": "textured-crop", "reason": "c"}]
        with _patch_pipeline(selection):
            with pytest.raises(ValueError):
                generate_recommendations(b"image", VALID_ANALYSIS)

    def test_raises_when_no_compatible_styles(self):
        """Sin estilos compatibles (valores inválidos) → error antes de llamar a la IA."""
        analysis = {"face_shape": "triangular", "hair_type": "unknown"}
        with patch(f"{_REPLICATE_PATH}.generate_image") as mock_gen:
            with pytest.raises(ValueError):
                generate_recommendations(b"image", analysis)
            mock_gen.assert_not_called()