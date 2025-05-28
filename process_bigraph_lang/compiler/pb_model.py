from dataclasses import dataclass

from typing import List, Dict, Any


@dataclass
class PBEntity:
    key: str
    path: list[str]  # the path to the entity, not including the key

    @property
    def full_path(self) -> list[str]:
        return self.path + [self.key]


@dataclass
class PBStore(PBEntity):
    data_type: str | dict[str, Any] | None = None
    value: Any | None = None


@dataclass
class PBEdge(PBEntity):
    address: str
    config_schema: dict[str, Any]
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    config_state: dict[str, Any]
    input_state: dict[str, Any]
    output_state: dict[str, Any]


@dataclass
class PBProcess(PBEdge):
    _type: str = "process"
    interval: float | None = None


@dataclass
class PBStep(PBEdge):
    _type: str = "step"


@dataclass
class PBModel:
    processes: List[PBProcess]
    steps: List[PBStep]
    stores: List[PBStore]
    types: List[Dict[str, Any]]
