from dataclasses import dataclass

from typing import Optional, List, Dict, Any


@dataclass
class PBEntity:
    key: str
    path: list[str]  # the path to the entity, not including the key

    @property
    def full_path(self) -> list[str]:
        return self.path + [self.key]


@dataclass
class PBStore(PBEntity):
    data_type: str
    value: Optional[Any] = None


@dataclass
class PBEdge(PBEntity):
    address: str
    config: dict[str, Any]
    inputs: dict[str, Any]
    outputs: dict[str, Any]


@dataclass
class PBProcess(PBEdge):
    _type: str = "process"


@dataclass
class PBStep(PBEdge):
    _type: str = "step"


@dataclass
class PBModel:
    processes: List[PBProcess]
    steps: List[PBStep]
    stores: List[PBStore]
    types: List[Dict[str, Any]]
