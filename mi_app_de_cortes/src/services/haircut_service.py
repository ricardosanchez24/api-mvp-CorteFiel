from io import BytesIO
from PIL import Image
from mi_app_de_cortes.src.clients.ai_client import ai_client
from mi_app_de_cortes.src.clients.replicate_client import ReplicateClient
from mi_app_de_cortes.src.services.styles_data import (
    get_all_styles,
    get_style_by_id,
    get_style_prompt,
    get_styles_by_face_shape,
)
from mi_app_de_cortes.src.models.recommend import Recommendation


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FORMATS = {"image/jpeg", "image/png"}


def validate_image(image_bytes: bytes, content_type: str) -> None:
    if content_type not in ALLOWED_FORMATS:
        raise ValueError(f"Invalid format. Allowed: JPG, PNG")

    if len(image_bytes) > MAX_FILE_SIZE:
        raise ValueError("Image exceeds 10MB limit")

    try:
        img = Image.open(BytesIO(image_bytes))
        img.verify()
    except Exception:
        raise ValueError("Corrupted or invalid image file")


def analyze_face(image_bytes: bytes, content_type: str) -> dict:
    validate_image(image_bytes, content_type)
    return ai_client.analyze_image(image_bytes, content_type)


def generate_recommendations(image_bytes: bytes, analysis: dict) -> list[Recommendation]:
    """Generate 3 haircut recommendations with images based on face shape."""
    face_shape = analysis.get("face_shape", "oval")
    replicate_client = ReplicateClient()
    styles = get_styles_by_face_shape(face_shape)[:3]
    recommendations = []

    for style in styles:
        prompt = get_style_prompt(style["id"], face_shape)
        image_result = replicate_client.generate_image(prompt, image_bytes)
        recommendations.append(Recommendation(
            style_id=style["id"],
            style_name=style["name"],
            description=style["description"],
            image_url=image_result,
        ))

    return recommendations
