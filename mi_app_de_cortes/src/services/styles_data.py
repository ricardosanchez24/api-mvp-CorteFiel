"""Styles data module - Feature 002
Catálogo de estilos de cabello cargado desde styles_data.json (data file).
Cada estilo lleva un prompt_template autocontenido (no se concatenan datos
externos al prompt: el diseño evita la fragilidad del enfoque anterior).

Los comentarios/docs están en español e inglés.
"""

import json
from pathlib import Path
from typing import Optional

_DATA_FILE = Path(__file__).parent / "styles_data.json"

_REQUIRED_FIELDS = {
    "id",
    "name",
    "description",
    "prompt_template",
    "face_shapes",
    "hair_types",
}
_ALLOWED_FACE_SHAPES = {"oval", "round", "square", "heart", "oblong"}
_ALLOWED_HAIR_TYPES = {"straight", "wavy", "curly", "coily"}


def _load_styles() -> list[dict]:
    """Load and validate the catalog from styles_data.json.
    Fails fast at import time if the file is missing or invalid."""
    if not _DATA_FILE.exists():
        raise FileNotFoundError(f"Catalog file not found: {_DATA_FILE}")

    try:
        with open(_DATA_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {_DATA_FILE}: {exc}")

    styles = data.get("styles", [])
    if not isinstance(styles, list) or not styles:
        raise ValueError("styles_data.json must contain a non-empty 'styles' list")

    seen_ids: set[str] = set()
    for style in styles:
        if not isinstance(style, dict):
            raise ValueError("Each catalog entry must be an object")

        missing = _REQUIRED_FIELDS - style.keys()
        if missing:
            raise ValueError(f"Style {style.get('id', '?')} is missing fields: {missing}")

        style_id = style["id"]
        if style_id in seen_ids:
            raise ValueError(f"Duplicate style id: {style_id}")
        seen_ids.add(style_id)

        invalid_shapes = set(style["face_shapes"]) - _ALLOWED_FACE_SHAPES
        if invalid_shapes:
            raise ValueError(
                f"Style '{style_id}' has invalid face_shapes: {invalid_shapes}"
            )

        invalid_hair = set(style["hair_types"]) - _ALLOWED_HAIR_TYPES
        if invalid_hair:
            raise ValueError(
                f"Style '{style_id}' has invalid hair_types: {invalid_hair}"
            )

    return styles


# Load once at import time: validation happens at startup (fail fast).
_STYLES: list[dict] = _load_styles()


def get_all_styles() -> list[dict]:
    """Return all available styles."""
    return _STYLES


def get_style_by_id(style_id: str) -> Optional[dict]:
    """Return a specific style by its ID, or None if it does not exist."""
    for style in _STYLES:
        if style["id"] == style_id:
            return style
    return None


def get_styles_by_face_shape(face_shape: str) -> list[dict]:
    """Return styles compatible with a specific face shape."""
    return [s for s in _STYLES if face_shape in s["face_shapes"]]


def get_styles_by_hair_type(hair_type: str) -> list[dict]:
    """Return styles compatible with a specific hair type."""
    return [s for s in _STYLES if hair_type in s["hair_types"]]


def get_compatible_styles(face_shape: str, hair_type: str) -> list[dict]:
    """Return styles compatible with both the face shape and the hair type."""
    if face_shape not in _ALLOWED_FACE_SHAPES or hair_type not in _ALLOWED_HAIR_TYPES:
        return []
    return [
        s
        for s in _STYLES
        if face_shape in s["face_shapes"] and hair_type in s["hair_types"]
    ]