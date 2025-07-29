"""Unit tests for configuration management."""

import pytest

from app.config import Settings


@pytest.mark.unit
class TestSettings:
    """Tests for Settings configuration."""

    def test_default_settings(self) -> None:
        """Test default settings values."""
        settings = Settings()
        assert settings.app_name == "Ollama OpenAI Proxy"
        assert settings.app_version == "0.1.0"
        assert settings.environment == "development"
        assert settings.host == "0.0.0.0"
        assert settings.port == 11434
        assert settings.log_level == "INFO"

    def test_settings_model_config(self) -> None:
        """Test settings model configuration."""
        assert Settings.model_config["env_prefix"] == "APP_"
        assert Settings.model_config["case_sensitive"] is False
        assert Settings.model_config["env_file"] == ".env"

    def test_settings_type_annotations(self) -> None:
        """Test settings have proper type annotations."""
        settings = Settings()
        assert isinstance(settings.app_name, str)
        assert isinstance(settings.app_version, str)
        assert isinstance(settings.environment, str)
        assert isinstance(settings.host, str)
        assert isinstance(settings.port, int)
        assert isinstance(settings.log_level, str)
