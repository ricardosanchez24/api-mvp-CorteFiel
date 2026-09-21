"""Tests for replicate_client module - Feature 002"""

import os
from unittest.mock import MagicMock, patch
import pytest

from mi_app_de_cortes.src.clients.replicate_client import ReplicateClient


class TestReplicateClient:
    """Tests for ReplicateClient Singleton"""

    def test_is_singleton(self):
        client1 = ReplicateClient()
        client2 = ReplicateClient()
        assert client1 is client2

    def test_has_generate_image_method(self):
        client = ReplicateClient()
        assert hasattr(client, "generate_image")

    def test_generate_image_returns_bytes(self):
        client = ReplicateClient()
        with patch.object(client, "generate_image", return_value=b"fake_image_bytes"):
            result = client.generate_image("fake_prompt", b"fake_image")
            assert isinstance(result, bytes)


class TestGenerateImage:
    """Tests for generate_image function"""

    def test_returns_bytes(self):
        client = ReplicateClient()
        with patch("mi_app_de_cortes.src.clients.replicate_client.replicate") as mock_replicate:
            mock_replicate.run.return_value = "data:image/png;base64,fakebase64data"
            result = client.generate_image("prompt", b"image_data")
            assert isinstance(result, bytes)

    def test_calls_replicate_api(self):
        client = ReplicateClient()
        with patch("mi_app_de_cortes.src.clients.replicate_client.replicate") as mock_replicate:
            mock_replicate.run.return_value = "data:image/png;base64,fakebase64data"
            client.generate_image("test_prompt", b"test_image")
            mock_replicate.run.assert_called_once()

    def test_handles_api_error(self):
        client = ReplicateClient()
        with patch("mi_app_de_cortes.src.clients.replicate_client.replicate") as mock_replicate:
            mock_replicate.run.side_effect = Exception("API Error")
            with pytest.raises(Exception) as exc_info:
                client.generate_image("prompt", b"image")
            assert "API Error" in str(exc_info.value)

    def test_returns_bytes_when_output_is_url(self):
        """Si Replicate devuelve una URL, el cliente la descarga y devuelve bytes."""
        client = ReplicateClient()
        with patch("mi_app_de_cortes.src.clients.replicate_client.replicate") as mock_replicate:
            mock_replicate.run.return_value = "https://example.com/img.png"
            with patch(
                "mi_app_de_cortes.src.clients.replicate_client.urllib.request.urlopen"
            ) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = b"PNG-DATA"
                result = client.generate_image("prompt", b"image")
            assert result == b"PNG-DATA"

    def test_handles_list_output(self):
        """Algunos modelos devuelven lista [url]; se toma el primer elemento."""
        client = ReplicateClient()
        with patch("mi_app_de_cortes.src.clients.replicate_client.replicate") as mock_replicate:
            mock_replicate.run.return_value = ["data:image/png;base64,aGVsbG8="]
            result = client.generate_image("prompt", b"image")
        assert result == b"hello"


class TestGenerateImageRetry:
    """Política de errores (decisión del usuario): fail-all con 1 retry."""

    def test_retries_once_and_succeeds(self):
        client = ReplicateClient()
        with patch("mi_app_de_cortes.src.clients.replicate_client.replicate") as mock_replicate:
            mock_replicate.run.side_effect = [
                Exception("API Error"),
                "data:image/png;base64,aGVsbG8g",
            ]
            result = client.generate_image("prompt", b"image", retries=1)
            assert result == b"hello "
            assert mock_replicate.run.call_count == 2

    def test_gives_up_after_retries(self):
        client = ReplicateClient()
        with patch("mi_app_de_cortes.src.clients.replicate_client.replicate") as mock_replicate:
            mock_replicate.run.side_effect = Exception("API Error")
            with pytest.raises(Exception) as exc_info:
                client.generate_image("prompt", b"image", retries=1)
            assert "API Error" in str(exc_info.value)
            assert mock_replicate.run.call_count == 2
