"""Replicate client module - Feature 002
Singleton pattern + retry (1 reintento) + normalización del output a bytes reales.

El modelo de Replicate puede responder con una URL, un data URI base64 o bytes;
esta capa garantiza que generate_image() siempre devuelva los bytes de la imagen.
"""

import base64
import urllib.request

import replicate

_MODEL = "google/nano-banana-pro"


class ReplicateClient:
    """Singleton client for Replicate API."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def generate_image(self, prompt: str, image_data: bytes, retries: int = 1) -> bytes:
        """Edita la imagen con Replicate y devuelve los bytes de la imagen resultante.

        Política de errores (decisión del usuario): fail-all con 1 retry.
        """
        last_error: Exception | None = None
        for _ in range(retries + 1):
            try:
                output = replicate.run(
                    _MODEL,
                    input={"prompt": prompt, "image": image_data},
                )
                return self._to_bytes(output)
            except Exception as exc:  # noqa: BLE001 - el error se propaga al job
                last_error = exc
        raise last_error  # type: ignore[misc]

    def _to_bytes(self, output) -> bytes:
        """Normaliza la salida de Replicate a bytes reales de imagen."""
        if isinstance(output, bytes):
            return output
        if isinstance(output, list):
            if not output:
                raise ValueError("Replicate returned an empty output list")
            return self._to_bytes(output[0])
        if isinstance(output, str):
            if output.startswith("data:"):
                # Formato: "data:image/png;base64,<data>"
                encoded = output.split(",", 1)[1]
                encoded += "=" * (-len(encoded) % 4)  # padding seguro
                return base64.b64decode(encoded)
            if output.startswith("http"):
                with urllib.request.urlopen(output, timeout=30) as resp:
                    return resp.read()
            raise ValueError(f"Unexpected Replicate output string: {output[:80]}")
        raise ValueError(f"Unexpected Replicate output type: {type(output)}")