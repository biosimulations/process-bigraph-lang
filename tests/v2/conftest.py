from typing import Any

import process_bigraph as pg  # type: ignore[import-untyped]
import pytest

from tests.fixtures.test_registry.spatio_flux import register_types


@pytest.fixture
def core() -> Any:
    return pg.allocate_core()


@pytest.fixture
def spatio_core() -> Any:
    core = pg.allocate_core()
    register_types(core)
    return core
