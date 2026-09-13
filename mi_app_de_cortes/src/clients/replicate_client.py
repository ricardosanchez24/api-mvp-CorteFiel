"""Replicate client module - Feature 002
Singleton pattern for Replicate API integration.
"""

import os
import replicate


class ReplicateClient:
    """Singleton client for Replicate API."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def generate_image(self, prompt: str, image_data: bytes) -> bytes:
        """Generate an image using Replicate API."""
        output = replicate.run(
            "google/nano-banana-pro",
            input={"prompt": prompt, "image": image_data},
        )
        if isinstance(output, str):
            return output.encode("utf-8")
        return output
