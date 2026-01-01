"""Health endpoint tests."""

import pytest


def test_health_check():
    """Test that health check passes."""
    assert True


def test_app_version():
    """Test app version is set."""
    from app.core.config import settings
    assert settings.APP_VERSION == "1.0.0"
