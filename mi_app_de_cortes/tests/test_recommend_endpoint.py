"""Tests for async POST /api/recommend + GET polling - Feature 002.

El flujo es asíncrono: POST responde 202 con job_id y el resultado se
consulta por polling con GET /api/recommend/{job_id}.
"""

import io
import time
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image

from mi_app_de_cortes.app import app
from mi_app_de_cortes.src.models.recommend import Recommendation

client = TestClient(app)

VALID_ANALYSIS = '{"face_shape": "oval", "hair_type": "straight", "confidence": "high"}'
LOW_CONFIDENCE = '{"face_shape": "oval", "confidence": "low"}'


def _png_bytes() -> bytes:
    """Un PNG válido real (PIL) para que validate_image pase de verdad."""
    buf = io.BytesIO()
    Image.new("RGB", (16, 16), (200, 100, 50)).save(buf, "PNG")
    return buf.getvalue()


def _make_recommendation(style_id: str, style_name: str) -> Recommendation:
    return Recommendation(
        style_id=style_id,
        style_name=style_name,
        description="Test",
        reason="Razón de prueba",
        image_base64="aGVsbG8=",
    )


def _fake_recommendations() -> list[Recommendation]:
    return [
        _make_recommendation("fade", "Fade Clásico"),
        _make_recommendation("undercut", "Undercut Clásico"),
        _make_recommendation("textured-crop", "Textured Crop"),
    ]


def _wait_for_job(job_id: str, timeout: float = 5.0) -> dict:
    """Polling helper: espera a que el job termine (completed/failed)."""
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        resp = client.get(f"/api/recommend/{job_id}")
        last = resp.json()
        if last["status"] in ("completed", "failed"):
            return last
        time.sleep(0.05)
    raise AssertionError(f"Job did not finish in time; last status: {last}")


class TestRecommendAsync:
    """POST /api/recommend devuelve 202 y encola un job."""

    def test_post_returns_202_with_job(self):
        with patch(
            "mi_app_de_cortes.src.services.haircut_service.generate_recommendations"
        ) as mock_gen:
            mock_gen.return_value = _fake_recommendations()
            response = client.post(
                "/api/recommend",
                files={"file": ("face.png", _png_bytes(), "image/png")},
                data={"analysis": VALID_ANALYSIS},
            )
            assert response.status_code == 202
            body = response.json()
            assert body["status"] == "pending"
            assert body["job_id"]
            assert body["status_url"] == f"/api/recommend/{body['job_id']}"

    def test_job_completes_with_3_recommendations(self):
        with patch(
            "mi_app_de_cortes.src.services.haircut_service.generate_recommendations"
        ) as mock_gen:
            mock_gen.return_value = _fake_recommendations()
            response = client.post(
                "/api/recommend",
                files={"file": ("face.png", _png_bytes(), "image/png")},
                data={"analysis": VALID_ANALYSIS},
            )
            body = _wait_for_job(response.json()["job_id"])
            assert body["status"] == "completed"
            assert len(body["recommendations"]) == 3
            assert mock_gen.call_count == 1

    def test_job_failed_reports_error(self):
        with patch(
            "mi_app_de_cortes.src.services.haircut_service.generate_recommendations"
        ) as mock_gen:
            mock_gen.side_effect = RuntimeError("boom")
            response = client.post(
                "/api/recommend",
                files={"file": ("face.png", _png_bytes(), "image/png")},
                data={"analysis": VALID_ANALYSIS},
            )
            body = _wait_for_job(response.json()["job_id"])
            assert body["status"] == "failed"
            assert "boom" in body["error"]

    def test_get_unknown_job_returns_404(self):
        response = client.get("/api/recommend/no-such-job")
        assert response.status_code == 404


class TestRecommendValidations:
    """Validaciones del endpoint: analysis, gate de confidence, formato."""

    def test_invalid_analysis_json_returns_400(self):
        response = client.post(
            "/api/recommend",
            files={"file": ("face.png", _png_bytes(), "image/png")},
            data={"analysis": "not-a-json"},
        )
        assert response.status_code == 400

    def test_missing_face_shape_returns_400(self):
        response = client.post(
            "/api/recommend",
            files={"file": ("face.png", _png_bytes(), "image/png")},
            data={"analysis": '{"confidence": "high"}'},
        )
        assert response.status_code == 400

    def test_low_confidence_returns_400(self):
        """Gate de cara: confidence 'low' del análisis de Feature 001 → 400."""
        response = client.post(
            "/api/recommend",
            files={"file": ("face.png", _png_bytes(), "image/png")},
            data={"analysis": LOW_CONFIDENCE},
        )
        assert response.status_code == 400
        assert "confidence" in response.json()["detail"].lower()

    def test_missing_analysis_returns_422(self):
        response = client.post(
            "/api/recommend",
            files={"file": ("face.png", _png_bytes(), "image/png")},
        )
        assert response.status_code == 422

    def test_missing_file_returns_422(self):
        response = client.post(
            "/api/recommend",
            data={"analysis": VALID_ANALYSIS},
        )
        assert response.status_code == 422

    def test_invalid_format_returns_400(self):
        response = client.post(
            "/api/recommend",
            files={"file": ("face.txt", b"fake", "text/plain")},
            data={"analysis": VALID_ANALYSIS},
        )
        assert response.status_code == 400