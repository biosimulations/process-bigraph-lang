"""
TODO: import all processes here and add to core
TODO -- make a "register_types" function that takes a core, registers all types and returns the core.
"""

from dataclasses import dataclass
from typing import Any

import numpy as np
from bigraph_schema.methods import apply  # type: ignore[import-untyped]
from bigraph_schema.schema import Array, Float  # type: ignore[import-untyped]

from tests.fixtures.test_registry.spatio_flux.processes import PROCESS_DICT


@dataclass(kw_only=True)
class PositiveFloat(Float):
    """A float that accumulates updates and is clamped to be non-negative."""


@apply.dispatch
def _apply_positive_float(schema: PositiveFloat, state: Any, update: Any, path: Any) -> tuple[Any, list[Any]]:
    if update is None:
        return state, []
    return max(0.0, state + update), []


@dataclass(kw_only=True)
class PositiveArray(Array):
    """An array whose updates are accumulated and clamped elementwise to be non-negative."""


@apply.dispatch
def _apply_positive_array(schema: PositiveArray, state: Any, update: Any, path: Any) -> tuple[Any, list[Any]]:
    if update is None:
        return state, []
    return np.maximum(0.0, state + update), []


positive_float = PositiveFloat


bounds_type = {"lower": "maybe[float]", "upper": "maybe[float]"}


particle_type = {
    "id": "string",
    "position": "tuple[float,float]",
    "size": "float",
    "mass": {"_type": "float", "_default": 1.0},
    "local": "map[float]",
    "exchange": "map[float]",  # {mol_id: delta_value}
}

boundary_side = "enum[left,right,top,bottom]"


substrate_role_type = "enum[reactant,product,enzyme]"
kinetics_type = {"vmax": "float", "kcat": "float", "role": "substrate_role"}
reaction_type = "map[kinetics]"


TYPES_DICT = {
    "positive_float": positive_float,
    "positive_array": PositiveArray,
    "bounds": bounds_type,
    "particle": particle_type,
    "boundary_side": boundary_side,
    "substrate_role": substrate_role_type,
    "kinetics": kinetics_type,
    "reaction": reaction_type,
}


def register_types(core: Any) -> Any:
    core.register_types(TYPES_DICT)
    core.register_links(PROCESS_DICT)
    return core
