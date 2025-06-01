from dataclasses import dataclass

from typing import List, Dict, Any, Literal


@dataclass
class PBEntity:
    key: str
    path: list[str]  # the path to the entity, not including the key

    @property
    def full_path(self) -> list[str]:
        return self.path + [self.key]


@dataclass
class PBCollectionType:
    coll_type: Literal["array"] | Literal["map"] = "map"


@dataclass
class PBStoreSchema(PBEntity):
    collection_type: PBCollectionType | None = None
    data_type: str | dict[str, Any] | None = None
    default_value: Any | None = None


@dataclass
class PBStoreState(PBEntity):
    store_schema: PBStoreSchema | None
    value: Any | None = None


@dataclass
class PBEdgeSchema(PBEntity):
    collection_info: PBCollectionType | None
    address: str
    config_schema: dict[str, Any]
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    default_config_state: dict[str, Any]
    default_input_state: dict[str, Any]
    default_output_state: dict[str, Any]


@dataclass
class PBEdgeState(PBEntity):
    address: str
    config_state: dict[str, Any]
    input_state: dict[str, Any]
    output_state: dict[str, Any]


@dataclass
class PBProcessSchema(PBEdgeSchema):
    _type: str = "process"
    default_interval: float | None = None


@dataclass
class PBProcessState(PBEdgeState):
    process_schema: PBProcessSchema
    _type: str = "process"
    interval: float | None = None


@dataclass
class PBStepSchema(PBEdgeSchema):
    _type: str = "step"


@dataclass
class PBStepState(PBEdgeState):
    step_schema: PBStepSchema
    _type: str = "step"


@dataclass
class PBModel:
    process_schemas: List[PBProcessSchema]
    process_states: List[PBProcessState]
    step_schemas: List[PBStepSchema]
    step_states: List[PBStepState]
    store_schemas: List[PBStoreSchema]
    store_states: List[PBStoreState]
    types: List[Dict[str, Any]]
