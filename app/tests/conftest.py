import pytest

from settings.config import Config


@pytest.fixture
def config():
    """Fixture providing config instance for tests."""
    return Config()
