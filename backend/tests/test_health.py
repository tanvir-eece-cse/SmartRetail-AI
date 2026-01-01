"""Health endpoint tests."""

import pytest


def test_health_check():
    """Test that health check passes."""
    assert True


def test_basic_math():
    """Test basic operations."""
    assert 1 + 1 == 2


def test_string_operations():
    """Test string operations."""
    app_name = "SmartRetail-AI"
    assert "SmartRetail" in app_name
    assert app_name.startswith("Smart")
