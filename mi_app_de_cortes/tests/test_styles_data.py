"""Tests for styles_data module - Feature 002"""

from mi_app_de_cortes.src.services.styles_data import (
    get_all_styles,
    get_style_by_id,
    get_style_prompt,
)


class TestGetAllStyles:
    """Tests for get_all_styles function"""

    def test_returns_list(self):
        result = get_all_styles()
        assert isinstance(result, list)

    def test_returns_at_least_3_styles(self):
        result = get_all_styles()
        assert len(result) >= 3

    def test_each_style_has_required_fields(self):
        result = get_all_styles()
        for style in result:
            assert "id" in style
            assert "name" in style
            assert "description" in style
            assert "face_shapes" in style
            assert "hair_types" in style


class TestGetStyleById:
    """Tests for get_style_by_id function"""

    def test_returns_style_when_exists(self):
        result = get_style_by_id("undercut")
        assert result is not None
        assert result["id"] == "undercut"

    def test_returns_none_when_not_exists(self):
        result = get_style_by_id("nonexistent-style")
        assert result is None


class TestGetStylePrompt:
    """Tests for get_style_prompt function"""

    def test_returns_string(self):
        result = get_style_prompt("undercut", "oval")
        assert isinstance(result, str)

    def test_returns_long_prompt(self):
        result = get_style_prompt("undercut", "oval")
        assert len(result) > 50

    def test_contains_style_name(self):
        result = get_style_prompt("undercut", "oval")
        assert "undercut" in result.lower()

    def test_contains_face_shape(self):
        result = get_style_prompt("undercut", "oval")
        assert "oval" in result.lower()
