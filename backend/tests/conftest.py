"""Pytest configuration and fixtures."""

import pytest
from typing import AsyncGenerator


@pytest.fixture
def anyio_backend():
    return "asyncio"
