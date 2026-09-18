from io import BytesIO
from PIL import Image
from mi_app_de_cortes.src.clients.ai_client import ai_client
from mi_app_de_cortes.src.clients.replicate_client import ReplicateClient
from mi_app_de_cortes.src.services.styles_data import (
    get_all_styles,
    get_style_by_id,
    get_style_prompt,
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
    """Generate haircut recommendations with images based on AI analysis."""
    face_shape = analysis.get("face_shape", "oval")
    recommended_styles = analysis.get("recommended_styles", [])
    replicate_client = ReplicateClient()
    recommendations = []

    for style_rec in recommended_styles:
        style_id = style_rec["id"]
        reason = style_rec["reason"]
        style_data = get_style_by_id(style_id)
        if style_data is None:
            continue
        prompt = get_style_prompt(style_id, face_shape)
        image_result = replicate_client.generate_image(prompt, image_bytes)
        recommendations.append(Recommendation(
            style_id=style_id,
            style_name=style_data["name"],
            description=style_data["description"],
            reason=reason,
            image_url=image_result,
        ))

    return recommendations
