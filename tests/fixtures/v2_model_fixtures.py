from pathlib import Path

import pytest


@pytest.fixture
def sbml_path_caravagna2010() -> Path:
    """Fixture for a model file."""
    return Path(__file__).parent / "data" / "compiler" / "Caravagna2010" / "Caravagna2010.xml"


@pytest.fixture
def model_path_caravagna2010() -> Path:
    """Fixture for a model file."""
    return Path(__file__).parent / "data" / "compiler" / "Caravagna2010" / "caravagna.pblang"
