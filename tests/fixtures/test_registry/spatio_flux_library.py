from typing import Any

from bigraph_schema import default  # type: ignore[import-untyped]
from process_bigraph import ProcessTypes  # type: ignore[import-untyped]
from spatio_flux import processes  # type: ignore[import-untyped]


def apply_non_negative(
    _schema: dict[str, Any],
    current: float,
    update: float,
    _top_schema: dict[str, Any],
    _top_state: dict[str, Any],
    _path: list[str],
    _core: ProcessTypes,
) -> float:
    new_value = current + update
    return max(0, new_value)


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

PROCESS_DICT = processes.PROCESS_DICT.copy()
