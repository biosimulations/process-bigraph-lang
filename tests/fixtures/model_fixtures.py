from pathlib import Path

import pytest


@pytest.fixture
def model_path_abc() -> Path:
    """
    Fixture that provides the path to the ABC model file.
    """
    return Path(__file__).parent / "models" / "abc_model.pblang"


@pytest.fixture
def model_path_abc_error() -> Path:
    """
    Fixture that provides the path to the ABC model file.
    """
    return Path(__file__).parent / "models" / "abc_model.pblang"


@pytest.fixture
def model_path_spatio_flux() -> Path:
    """
    Fixture that provides the path to the Spatio-Flux model file.
    """
    return Path(__file__).parent / "models" / "spatio_flux.pblang"
