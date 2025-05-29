from typing import Any

from process_bigraph_lang.compiler.pb_model import PBModel


def assemble_pb(pb_model: PBModel) -> dict[str, Any]:
    doc: dict[str, Any] = dict(composition={}, state={})
    for store_schema in pb_model.store_schemas:
        # TODO: handle collection_type properly
        if store_schema.default_value is not None:
            if store_schema.collection_type is None:
                set_value_at_path(
                    doc["composition"], store_schema.full_path + ["_default"], value=store_schema.default_value
                )
                if store_schema.data_type:
                    set_value_at_path(doc["composition"], store_schema.full_path + ["_type"], value=store_schema.data_type)
            elif store_schema.collection_type == "map":
                if store_schema.data_type:
                    set_value_at_path(doc["composition"], store_schema.full_path + ["_type"], value="map")
                    set_value_at_path(doc["composition"], store_schema.full_path + ["_value"], value=store_schema.data_type)
        elif store_schema.data_type:
            set_value_at_path(doc["composition"], store_schema.full_path, value=store_schema.data_type)

    for store_state in pb_model.store_states:
        if store_state.value is not None:
            set_value_at_path(doc["state"], store_state.full_path, value=store_state.value)
    for step_schema in pb_model.step_schemas:
        # TODO: handle collection_type properly
        address = step_schema.address
        if not address.startswith("local:"):
            address = "local:!" + address
        address_dict = dict(_type="quote", _default=address)
        step_schema_dict: dict[str, Any] = dict(_type=step_schema._type, address=address_dict)
        if step_schema.config_schema:
            step_schema_dict["_config"] = step_schema.config_schema
        if step_schema.input_schema:
            step_schema_dict["_inputs"] = step_schema.input_schema
        if step_schema.output_schema:
            step_schema_dict["_outputs"] = step_schema.output_schema
        set_value_at_path(doc["composition"], step_schema.full_path, value=step_schema_dict)

    for step_state in pb_model.step_states:
        step_state_dict: dict[str, Any] = dict(_type=step_state._type)
        if step_state.config_state:
            step_state_dict["config"] = step_state.config_state
        if step_state.input_state:
            step_state_dict["inputs"] = step_state.input_state
        if step_state.output_state:
            step_state_dict["outputs"] = step_state.output_state
        set_value_at_path(doc["state"], step_state.full_path, value=step_state_dict)

    for process_schema in pb_model.process_schemas:
        address = process_schema.address
        if not address.startswith("local:"):
            address = "local:!" + address
        address_dict = dict(_type="quote", _default=address)
        process_schema_dict: dict[str, Any] = dict(_type=process_schema._type, address=address_dict)
        if process_schema.config_schema:
            process_schema_dict["_config"] = process_schema.config_schema
        if process_schema.input_schema:
            process_schema_dict["_inputs"] = process_schema.input_schema
        if process_schema.output_schema:
            process_schema_dict["_outputs"] = process_schema.output_schema
        # if process_schema.default_interval is not None:
        #     process_schema_dict["_interval"] = process_schema.default_interval
        set_value_at_path(doc["composition"], process_schema.full_path, value=process_schema_dict)

    for process_state in pb_model.process_states:
        process_state_dict: dict[str, Any] = dict(_type=process_state._type)
        if process_state.config_state:
            process_state_dict["config"] = process_state.config_state
        if process_state.input_state:
            process_state_dict["inputs"] = process_state.input_state
        if process_state.output_state:
            process_state_dict["outputs"] = process_state.output_state
        if process_state.interval is not None:
            process_state_dict["interval"] = process_state.interval
        set_value_at_path(doc["state"], process_state.full_path, value=process_state_dict)

    return doc


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
