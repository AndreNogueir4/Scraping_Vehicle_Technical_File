import pytest

@pytest.fixture
def automaker():
    return 'chevrolet'

@pytest.fixture
def model():
    return 's10'

@pytest.fixture
def href():
    return '/carros/chevrolet/s10-ltz-2-5-4x4-at-cd-2018'