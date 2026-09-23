from typing import Any

from process_bigraph_lang.compiler.pb_model import (
    PBCollectionType,
    PBEdgeSchema,
    PBEdgeState,
    PBModel,
    PBProcessSchema,
)


def assemble_pb(pb_model: PBModel) -> dict[str, Any]:
    """
    Assemble a process-bigraph (>= 1.8) composite document: {"schema": ..., "state": ...}.

    `schema` holds store types only. Each step/process is a node in `state` carrying its `address`
    (a plain `protocol:data` string), `config`, port types (`_inputs`/`_outputs`), wires and `interval`.
    A map of edges also gets a `{"_type": "map", "_value": <edge type>}` entry in `schema`.
    """
    doc: dict[str, Any] = dict(schema={}, state={})
    # An open store (a site) is typed by its site's _sort alone: process-bigraph (1.8.4) realizes a
    # store that also has a schema entry from that schema and silently ignores the unfilled site.
    open_paths = {tuple(s.full_path) for s in pb_model.store_states if _is_site(s.value)}
    for store_schema in pb_model.store_schemas:
        if tuple(store_schema.full_path) in open_paths:
            continue
        if store_schema.collection_type == PBCollectionType(coll_type="map"):
            if store_schema.data_type:
                set_value_at_path(doc["schema"], store_schema.path + ["_type"], value="map")
                set_value_at_path(doc["schema"], store_schema.path + ["_value"], value=store_schema.data_type)
        elif store_schema.collection_type is not None:
            raise ValueError(
                f"Unsupported collection type '{store_schema.collection_type}' for store schema '{store_schema.full_path}'"
            )
        elif store_schema.default_value is not None:
            set_value_at_path(
                doc["schema"],
                store_schema.full_path,
                value={"_type": store_schema.data_type, "_default": store_schema.default_value},
            )
        elif store_schema.data_type:
            set_value_at_path(doc["schema"], store_schema.full_path, value=store_schema.data_type)

    for store_state in pb_model.store_states:
        if store_state.value is not None:
            set_value_at_path(doc["state"], store_state.full_path, value=store_state.value)

    edges: list[tuple[PBEdgeSchema, list[PBEdgeState]]] = []
    for step_schema in pb_model.step_schemas:
        edges.append((step_schema, [s for s in pb_model.step_states if s.step_schema is step_schema]))
    for process_schema in pb_model.process_schemas:
        edges.append((process_schema, [s for s in pb_model.process_states if s.process_schema is process_schema]))
    for edge_schema, edge_states in edges:
        if edge_schema.collection_info is not None:
            if edge_schema.collection_info.coll_type != "map":
                raise ValueError(
                    f"Unsupported collection type '{edge_schema.collection_info}' for edge schema '{edge_schema.full_path}'"
                )
            set_value_at_path(
                doc["schema"], edge_schema.full_path, value={"_type": "map", "_value": _edge_type(edge_schema)}
            )
        for edge_state in edge_states:
            set_value_at_path(doc["state"], edge_state.full_path, value=_edge_node(edge_schema, edge_state))

    return doc


def edge_address(address: str) -> str:
    """A bare Python path becomes a portable `local:!` address; addresses with a protocol are kept."""
    return address if ":" in address else f"local:!{address}"


def site(sort: Any, default: Any = None) -> dict[str, Any]:
    """A template site: an open value of type `sort`, required unless it has a `default`."""
    node: dict[str, Any] = {"_type": "site", "_sort": sort}
    if default is not None:
        node["_default"] = default
    return node


def _is_site(value: Any) -> bool:
    return isinstance(value, dict) and value.get("_type") == "site"


def _face(edge_schema: PBEdgeSchema) -> dict[str, Any]:
    face: dict[str, Any] = {"_type": "link"}
    if edge_schema.input_schema:
        face["_inputs"] = edge_schema.input_schema
    if edge_schema.output_schema:
        face["_outputs"] = edge_schema.output_schema
    return face


def _edge_type(edge_schema: PBEdgeSchema) -> dict[str, Any]:
    edge_type: dict[str, Any] = {"_type": _edge_kind(edge_schema)}
    if edge_schema.input_schema:
        edge_type["_inputs"] = edge_schema.input_schema
    if edge_schema.output_schema:
        edge_type["_outputs"] = edge_schema.output_schema
    return edge_type


def _edge_kind(edge_schema: PBEdgeSchema) -> str:
    return "process" if isinstance(edge_schema, PBProcessSchema) else "step"


def _edge_node(edge_schema: PBEdgeSchema, edge_state: PBEdgeState) -> dict[str, Any]:
    address = edge_state.address or edge_schema.address
    node: dict[str, Any] = {
        **_edge_type(edge_schema),
        # an interface (no address) leaves its implementation open: an address site sorted by its face
        "address": edge_address(address) if address is not None else site(_face(edge_schema)),
    }
    config = {**edge_schema.default_config_state, **edge_state.config_state}
    if config:
        node["config"] = config
    inputs = {**edge_schema.default_input_state, **edge_state.input_state}
    if inputs:
        node["inputs"] = inputs
    outputs = {**edge_schema.default_output_state, **edge_state.output_state}
    if outputs:
        node["outputs"] = outputs
    interval = getattr(edge_state, "interval", None)
    if interval is None and isinstance(edge_schema, PBProcessSchema):
        interval = edge_schema.default_interval
    if interval is not None:
        node["interval"] = interval
    return node


def get_value_at_path(data: dict, keys: list[str]) -> Any:
    """Retrieve the value from a nested dictionary using a list of keys."""
    for key in keys:
        if not isinstance(data, dict) or key not in data:
            raise KeyError(f"Key path {' -> '.join(keys)} does not exist.")
        data = data[key]
    return data


def set_value_at_path(data: dict, keys: list[str], value: Any) -> None:
    """Set the value in a nested dictionary at the specified path."""
    for key in keys[:-1]:
        if key not in data or not isinstance(data[key], dict):
            data[key] = {}
        data = data[key]
    data[keys[-1]] = value
