"""Tests for job store y worker en background - Feature 002 (flujo asíncrono)."""

from unittest.mock import patch

from mi_app_de_cortes.src.models.recommend import JobStatus, Recommendation
from mi_app_de_cortes.src.services.recommend_job import job_store, process_job


def _rec(style_id: str = "fade") -> Recommendation:
    return Recommendation(
        style_id=style_id,
        style_name="Fade Clásico",
        description="Test",
        reason="Razón",
        image_base64="aGVsbG8=",
    )


class TestJobStore:
    """Tests del almacén en memoria (thread-safe)."""

    def test_create_job_returns_pending(self):
        job = job_store.create_job()
        assert job["status"] == JobStatus.PENDING
        assert job["error"] is None
        assert job["recommendations"] is None
        assert job["job_id"]

    def test_get_unknown_job_returns_none(self):
        assert job_store.get_job("no-such-job") is None

    def test_update_job_changes_status(self):
        job = job_store.create_job()
        updated = job_store.update_job(
            job["job_id"], status=JobStatus.PROCESSING
        )
        assert updated["status"] == JobStatus.PROCESSING
        assert job_store.get_job(job["job_id"])["status"] == JobStatus.PROCESSING

    def test_update_unknown_job_returns_none(self):
        assert job_store.update_job("no-such-job", status=JobStatus.FAILED) is None


class TestProcessJob:
    """Tests del worker: genera recomendaciones y guarda el resultado."""

    def test_success_sets_completed_with_recommendations(self):
        job = job_store.create_job()
        recommendations = [_rec("fade")] * 3
        with patch(
            "mi_app_de_cortes.src.services.recommend_job.haircut_service"
            ".generate_recommendations",
            return_value=recommendations,
        ):
            process_job(job["job_id"], b"image", {"face_shape": "oval"})
        updated = job_store.get_job(job["job_id"])
        assert updated["status"] == JobStatus.COMPLETED
        assert updated["recommendations"] == recommendations

    def test_failure_sets_failed_with_error(self):
        job = job_store.create_job()
        with patch(
            "mi_app_de_cortes.src.services.recommend_job.haircut_service"
            ".generate_recommendations",
            side_effect=RuntimeError("boom"),
        ):
            process_job(job["job_id"], b"image", {"face_shape": "oval"})
        updated = job_store.get_job(job["job_id"])
        assert updated["status"] == JobStatus.FAILED
        assert "boom" in updated["error"]
        assert updated["recommendations"] is None