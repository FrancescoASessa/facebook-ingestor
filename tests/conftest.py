import pytest

from app.observability import _reset_default_observability


@pytest.fixture(autouse=True)
def reset_observability():
    _reset_default_observability()
    yield
    _reset_default_observability()
