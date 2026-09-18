import os
from google import genai
from google.genai import types


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
            model="gemini-3.5-flash",
            contents=[
                "Analyze this face photo and extract the following information in JSON format: "
                "face_shape (oval, round, square, heart, oblong), "
                "hair_type (straight, wavy, curly, coily), "
                "hair_texture (fine, medium, thick), "
                "skin_tone (light, medium, dark), "
                "features (list of prominent facial features), "
                "confidence (high, medium, low), "
                "recommended_styles (list of 3 hairstyle recommendations with id and reason). "
                "Available styles: undercut, fade, textured-crop. "
                "For each recommended style, explain WHY it suits this person's face. "
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
                        "recommended_styles": types.Schema(
                            type=types.Type.ARRAY,
                            items=types.Schema(
                                type=types.Type.OBJECT,
                                properties={
                                    "id": types.Schema(type=types.Type.STRING),
                                    "reason": types.Schema(type=types.Type.STRING),
                                },
                            ),
                        ),
                    },
                    property_ordering=[
                        "face_shape",
                        "hair_type",
                        "hair_texture",
                        "skin_tone",
                        "features",
                        "confidence",
                        "recommended_styles",
                    ],
                ),
            ),
        )
        return response.parsed


ai_client = AIClient()
