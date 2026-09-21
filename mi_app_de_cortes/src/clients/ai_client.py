import os
from typing import Optional

from google import genai
from google.genai import types

_MODEL = "gemini-3.6-flash"


class AIClient:
    _instance = None
    client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_client(self):
        if self.client is None:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable is required")
            self.client = genai.Client(api_key=api_key)
        return self.client

    def analyze_image(self, image_bytes: bytes, mime_type: str) -> dict:
        client = self.get_client()
        response = client.models.generate_content(
            model=_MODEL,
            contents=[
                "Analyze this face photo and extract the following information in JSON format: "
                "face_shape (oval, round, square, heart, oblong), "
                "hair_type (straight, wavy, curly, coily), "
                "hair_texture (fine, medium, thick), "
                "skin_tone (light, medium, dark), "
                "features (list of prominent facial features), "
                "confidence (high, medium, low). "
                "Respond only in JSON format.",
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "face_shape": types.Schema(type=types.Type.STRING),
                        "hair_type": types.Schema(type=types.Type.STRING),
                        "hair_texture": types.Schema(type=types.Type.STRING),
                        "skin_tone": types.Schema(type=types.Type.STRING),
                        "features": types.Schema(
                            type=types.Type.ARRAY,
                            items=types.Schema(type=types.Type.STRING),
                        ),
                        "confidence": types.Schema(type=types.Type.STRING),
                    },
                    property_ordering=[
                        "face_shape",
                        "hair_type",
                        "hair_texture",
                        "skin_tone",
                        "features",
                        "confidence",
                    ],
                ),
            ),
        )
        return response.parsed

    def select_styles(
        self,
        candidates: list[dict],
        face_shape: str,
        hair_type: Optional[str],
        hair_texture: Optional[str],
        features: list[str],
    ) -> list[dict]:
        """La IA elige exactamente 3 estilos compatibles del catálogo, con razón.

        NO se usa skin_tone para recomendar (sesgo). Devuelve:
        [{"id": "<style_id>", "reason": "<por qué le queda>"}]
        """
        client = self.get_client()
        candidates_text = "\n".join(
            f"- {c['id']}: {c['name']} — {c['description']}" for c in candidates
        )
        prompt = (
            "You are a professional barber advisor for young men. "
            f"The person has: face_shape={face_shape}, "
            f"hair_type={hair_type or 'unknown'}, "
            f"hair_texture={hair_texture or 'unknown'}, "
            f"features={', '.join(features) if features else 'unknown'}. "
            "From the candidate styles below, choose exactly 3 that suit this "
            "person best. NEVER base your selection on skin tone. "
            "For each chosen style, explain in one sentence why it suits this face. "
            "Candidate styles:\n"
            f"{candidates_text}\n"
            "Respond only in JSON."
        )
        response = client.models.generate_content(
            model=_MODEL,
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "selected_styles": types.Schema(
                            type=types.Type.ARRAY,
                            items=types.Schema(
                                type=types.Type.OBJECT,
                                properties={
                                    "id": types.Schema(type=types.Type.STRING),
                                    "reason": types.Schema(type=types.Type.STRING),
                                },
                                required=["id", "reason"],
                            ),
                        ),
                    },
                    required=["selected_styles"],
                ),
            ),
        )
        parsed = response.parsed
        selected = (
            parsed.selected_styles
            if hasattr(parsed, "selected_styles")
            else parsed["selected_styles"]
        )
        if not isinstance(selected, list):
            raise ValueError("AI selection returned an invalid structure")
        return selected


ai_client = AIClient()