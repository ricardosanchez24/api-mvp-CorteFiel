"""Job store y worker en background - Feature 002 (flujo asíncrono).

Almacena los jobs de recomendación en memoria (dict + lock).
Trade-off aceptado (decisión del usuario): un reinicio del servidor pierde
los jobs en curso. El MVP es stateless; romper parcialmente ese principio
fue necesario para soportar la latencia de generación de imágenes (1-2 min).
"""

import asyncio
import threading
import uuid
from datetime import datetime, timezone
from typing import Optional

from mi_app_de_cortes.src.models.recommend import JobStatus
from mi_app_de_cortes.src.services import haircut_service


class JobStore:
    """Almacén en memoria (thread-safe) para jobs de recomendación."""

    def __init__(self) -> None:
        self._jobs: dict[str, dict] = {}
        self._lock = threading.Lock()

    def create_job(self) -> dict:
        job_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        job = {
            "job_id": job_id,
            "status": JobStatus.PENDING,
            "error": None,
            "recommendations": None,
            "created_at": now,
            "updated_at": now,
        }
        with self._lock:
            self._jobs[job_id] = job
        return job

    def get_job(self, job_id: str) -> Optional[dict]:
        with self._lock:
            return self._jobs.get(job_id)

    def update_job(self, job_id: str, **fields) -> Optional[dict]:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            job.update(fields)
            job["updated_at"] = datetime.now(timezone.utc).isoformat()
            return job


job_store = JobStore()


def process_job(job_id: str, image_bytes: bytes, analysis: dict) -> None:
    """Worker (hilo en background): genera las recomendaciones y guarda el
    resultado o el error en el job store."""
    try:
        job_store.update_job(job_id, status=JobStatus.PROCESSING)
        recommendations = haircut_service.generate_recommendations(image_bytes, analysis)
        job_store.update_job(
            job_id,
            status=JobStatus.COMPLETED,
            recommendations=recommendations,
        )
    except Exception as exc:  # noqa: BLE001 - el error viaja al cliente por API
        job_store.update_job(job_id, status=JobStatus.FAILED, error=str(exc))


# Referencias a los tasks para evitar que el garbage collector los elimine.
scheduled_tasks: set[asyncio.Task] = set()


def schedule_job(job_id: str, image_bytes: bytes, analysis: dict) -> None:
    """Ejecuta el job en un hilo en background sin bloquear el event loop."""
    task = asyncio.create_task(
        asyncio.to_thread(process_job, job_id, image_bytes, analysis)
    )
    scheduled_tasks.add(task)
    task.add_done_callback(scheduled_tasks.discard)