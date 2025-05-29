"""
TODO: import all processes here and add to core
TODO -- make a "register_types" function that takes a core, registers all types and returns the core.
"""

from typing import Any

from bigraph_schema import default  # type: ignore[import-untyped]
from process_bigraph import ProcessTypes  # type: ignore[import-untyped]

from tests.fixtures.test_registry.spatio_flux.processes import PROCESS_DICT


def apply_non_negative(
    schema: dict[str, Any],
    current: float,
    update: float,
    top_schema: dict[str, Any],
    top_state: dict[str, Any],
    path: list[str],
    core: ProcessTypes,
) -> float:
    new_value = current + update
    return max(0.0, new_value)


positive_float = {"_inherit": "float", "_apply": apply_non_negative}


bounds_type = {"lower": "maybe[float]", "upper": "maybe[float]"}


particle_type = {
    "id": "string",
    "position": "tuple[float,float]",
    "size": "float",
    "mass": default("float", 1.0),
    "local": "map[float]",
    "exchange": "map[float]",  # {mol_id: delta_value}
}

boundary_side = "enum[left,right,top,bottom]"


substrate_role_type = "enum[reactant,product,enzyme]"
kinetics_type = {"vmax": "float", "kcat": "float", "role": "substrate_role"}
reaction_type = "map[kinetics]"


TYPES_DICT = {
    "positive_float": positive_float,
    "bounds": bounds_type,
    "particle": particle_type,
    "boundary_side": boundary_side,
    "substrate_role": substrate_role_type,
    "kinetics": kinetics_type,
    "reaction": reaction_type,
}


def register_types(core: ProcessTypes) -> ProcessTypes:
    for type_name, type_schema in TYPES_DICT.items():
        core.register(type_name, type_schema)
    for process_name, process in PROCESS_DICT.items():
        core.register_process(process_name, process)
    return core
