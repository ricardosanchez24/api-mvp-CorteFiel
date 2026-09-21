"""Tests for styles_data module - Feature 002 (catálogo de 60 estilos)."""

from mi_app_de_cortes.src.services.styles_data import (
    get_all_styles,
    get_compatible_styles,
    get_style_by_id,
    get_styles_by_face_shape,
    get_styles_by_hair_type,
)

ALL_FACE_SHAPES = {"oval", "round", "square", "heart", "oblong"}
ALL_HAIR_TYPES = {"straight", "wavy", "curly", "coily"}
REQUIRED_FIELDS = {
    "id",
    "name",
    "description",
    "prompt_template",
    "face_shapes",
    "hair_types",
}
LEGACY_IDS = ("undercut", "fade", "textured-crop")


class TestGetAllStyles:
    """Tests for get_all_styles function."""

    def test_returns_list(self):
        result = get_all_styles()
        assert isinstance(result, list)

    def test_returns_at_least_60_styles(self):
        result = get_all_styles()
        assert len(result) >= 60

    def test_each_style_has_required_fields(self):
        for style in get_all_styles():
            assert REQUIRED_FIELDS.issubset(style), f"style '{style.get('id')}' missing fields"

    def test_ids_are_unique(self):
        ids = [s["id"] for s in get_all_styles()]
        assert len(ids) == len(set(ids))

    def test_covers_all_face_shapes(self):
        covered = set().union(*(s["face_shapes"] for s in get_all_styles()))
        assert covered == ALL_FACE_SHAPES

    def test_covers_all_hair_types(self):
        covered = set().union(*(s["hair_types"] for s in get_all_styles()))
        assert covered == ALL_HAIR_TYPES

    def test_every_style_has_non_empty_groups(self):
        for style in get_all_styles():
            assert style["face_shapes"], f"style '{style['id']}' has no face_shapes"
            assert style["hair_types"], f"style '{style['id']}' has no hair_types"

    def test_every_prompt_is_self_contained(self):
        """Cada prompt_template describe el corte por completo y solo toca el cabello."""
        for style in get_all_styles():
            template = style["prompt_template"]
            assert len(template) > 50, f"style '{style['id']}' prompt too short"
            assert "only modify the hair" in template.lower()


class TestGetStyleById:
    """Tests for get_style_by_id function."""

    def test_returns_style_when_exists(self):
        result = get_style_by_id("undercut")
        assert result is not None
        assert result["id"] == "undercut"

    def test_legacy_ids_still_exist(self):
        """Los 3 ids del pipeline viejo se mantienen durante la transición."""
        for style_id in LEGACY_IDS:
            assert get_style_by_id(style_id) is not None, f"legacy id '{style_id}' missing"

    def test_returns_none_when_not_exists(self):
        assert get_style_by_id("nonexistent-style") is None


class TestGetStylesByFaceShape:
    """Tests for get_styles_by_face_shape function."""

    def test_returns_only_matching_styles(self):
        for style in get_styles_by_face_shape("oval"):
            assert "oval" in style["face_shapes"]

    def test_every_face_shape_has_candidates(self):
        for shape in ALL_FACE_SHAPES:
            assert get_styles_by_face_shape(shape), f"no styles for face_shape '{shape}'"

    def test_returns_empty_for_invalid_shape(self):
        assert get_styles_by_face_shape("triangular") == []


class TestGetStylesByHairType:
    """Tests for get_styles_by_hair_type function."""

    def test_returns_only_matching_styles(self):
        for style in get_styles_by_hair_type("curly"):
            assert "curly" in style["hair_types"]

    def test_every_hair_type_has_candidates(self):
        for hair_type in ALL_HAIR_TYPES:
            assert get_styles_by_hair_type(hair_type), f"no styles for hair_type '{hair_type}'"

    def test_returns_empty_for_invalid_hair_type(self):
        assert get_styles_by_hair_type("unknown") == []


class TestGetCompatibleStyles:
    """Tests for get_compatible_styles function (face_shape + hair_type)."""

    def test_returns_non_empty_for_valid_combination(self):
        result = get_compatible_styles("oval", "straight")
        assert len(result) > 0

    def test_each_result_is_compatible(self):
        face_shape, hair_type = "oval", "straight"
        for style in get_compatible_styles(face_shape, hair_type):
            assert face_shape in style["face_shapes"]
            assert hair_type in style["hair_types"]

    def test_is_subset_of_each_single_filter(self):
        combined = {s["id"] for s in get_compatible_styles("oval", "straight")}
        by_shape = {s["id"] for s in get_styles_by_face_shape("oval")}
        by_hair = {s["id"] for s in get_styles_by_hair_type("straight")}
        assert combined <= by_shape
        assert combined <= by_hair

    def test_returns_empty_for_invalid_combination(self):
        assert get_compatible_styles("triangular", "unknown") == []