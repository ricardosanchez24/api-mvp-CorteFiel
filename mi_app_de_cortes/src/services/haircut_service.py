from io import BytesIO
from PIL import Image
from mi_app_de_cortes.src.clients.ai_client import ai_client


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
