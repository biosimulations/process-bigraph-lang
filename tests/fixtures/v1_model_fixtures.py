from pathlib import Path

import pytest


@pytest.fixture
def model_paths_add_floats_steps() -> tuple[Path, Path]:
    """Fixture for a model file."""
    return (
        Path(__file__).parent / "data" / "runtime" / "v1" / "add_floats_steps.pblang",
        Path(__file__).parent / "data" / "runtime" / "v1" / "add_floats_steps.pblang.ast.json",
    )


@pytest.fixture
def model_paths_add_floats_processes() -> tuple[Path, Path]:
    """Fixture for a model file."""
    return (
        Path(__file__).parent / "data" / "runtime" / "v1" / "add_floats_processes.pblang",
        Path(__file__).parent / "data" / "runtime" / "v1" / "add_floats_processes.pblang.ast.json",
    )
