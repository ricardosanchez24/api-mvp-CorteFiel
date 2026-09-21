import base64
from io import BytesIO

from PIL import Image

from mi_app_de_cortes.src.clients.ai_client import ai_client
from mi_app_de_cortes.src.clients.replicate_client import ReplicateClient
from mi_app_de_cortes.src.models.recommend import Recommendation
from mi_app_de_cortes.src.services.styles_data import (
    get_compatible_styles,
    get_style_by_id,
    get_styles_by_face_shape,
)


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FORMATS = {"image/jpeg", "image/png"}

N_RECOMMENDATIONS = 3


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


def _validate_selection(selected: list[dict]) -> None:
    """La IA debe devolver exactamente 3 ids, únicos y existentes en el catálogo."""
    if len(selected) != N_RECOMMENDATIONS:
        raise ValueError(
            f"AI must return exactly {N_RECOMMENDATIONS} styles, got {len(selected)}"
        )
    ids = [s.get("id") for s in selected]
    if len(set(ids)) != len(ids):
        raise ValueError("AI returned duplicate style ids")
    for style_id in ids:
        if get_style_by_id(style_id) is None:
            raise ValueError(f"AI returned unknown style id: {style_id}")


def generate_recommendations(image_bytes: bytes, analysis: dict) -> list[Recommendation]:
    """Orquesta la recomendación asíncrona:

    1) Filtra el catálogo por face_shape + hair_type del análisis (Feature 001).
    2) La IA elige 3 estilos compatibles con su razón (no usa skin_tone).
    3) Replicate edita SOLO el cabello de la foto del usuario por estilo (1 retry).
    4) Entrega las imágenes en base64 inline.
    """
    face_shape = analysis.get("face_shape", "oval")
    hair_type = analysis.get("hair_type")
    hair_texture = analysis.get("hair_texture")
    features = analysis.get("features", [])

    candidates = (
        get_compatible_styles(face_shape, hair_type)
        if hair_type
        else get_styles_by_face_shape(face_shape)
    )
    if not candidates:
        raise ValueError(
            f"No catalog styles compatible with face_shape='{face_shape}' "
            f"and hair_type='{hair_type}'"
        )

    selected = ai_client.select_styles(
        candidates,
        face_shape=face_shape,
        hair_type=hair_type,
        hair_texture=hair_texture,
        features=features,
    )
    _validate_selection(selected)

    replicate_client = ReplicateClient()
    recommendations: list[Recommendation] = []
    for item in selected:
        style = get_style_by_id(item["id"])
        prompt = style["prompt_template"]
        edited_bytes = replicate_client.generate_image(prompt, image_bytes)
        image_b64 = base64.b64encode(edited_bytes).decode("utf-8")
        recommendations.append(
            Recommendation(
                style_id=item["id"],
                style_name=style["name"],
                description=style["description"],
                reason=item["reason"],
                image_base64=image_b64,
            )
        )
    return recommendations