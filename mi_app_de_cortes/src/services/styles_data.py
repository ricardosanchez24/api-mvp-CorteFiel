"""Styles data module - Feature 002
Catálogo de estilos de cabello con prompts para generación de imágenes.
"""

from typing import Optional


# Catálogo de estilos
STYLES = [
    {
        "id": "undercut",
        "name": "Undercut",
        "description": "Laterales cortos con la parte superior larga y peinada hacia atrás",
        "face_shapes": ["oval", "heart"],
        "hair_types": ["straight", "wavy"],
        "prompt_template": (
            "Change the hairstyle to an undercut: short sides with longer top "
            "styled backwards. Keep the same face, skin tone, and features. "
            "Only modify the hair."
        ),
    },
    {
        "id": "fade",
        "name": "Fade",
        "description": "Transición gradual de largo a corto en los laterales",
        "face_shapes": ["oval", "round", "square"],
        "hair_types": ["straight", "wavy"],
        "prompt_template": (
            "Change the hairstyle to a fade cut: gradual transition from long "
            "to short on the sides. Keep the same face, skin tone, and features. "
            "Only modify the hair."
        ),
    },
    {
        "id": "textured-crop",
        "name": "Textured Crop",
        "description": "Corte corto con textura en la parte superior, mechones hacia adelante",
        "face_shapes": ["oval", "square"],
        "hair_types": ["straight", "wavy", "curly"],
        "prompt_template": (
            "Change the hairstyle to a textured crop: short cut with texture "
            "on top, hair strands pointing forward. Keep the same face, "
            "skin tone, and features. Only modify the hair."
        ),
    },
]


def get_all_styles() -> list[dict]:
    """Return all available styles."""
    return STYLES


def get_style_by_id(style_id: str) -> Optional[dict]:
    """Return a specific style by its ID."""
    for style in STYLES:
        if style["id"] == style_id:
            return style
    return None


def get_styles_by_face_shape(face_shape: str) -> list[dict]:
    """Return styles compatible with a specific face shape."""
    return [s for s in STYLES if face_shape in s["face_shapes"]]


def get_style_prompt(style_id: str, face_shape: str) -> str:
    """Return the prompt for generating an image with a specific style."""
    style = get_style_by_id(style_id)
    if style is None:
        return ""
    return f"{style['prompt_template']} The face shape is {face_shape}."
