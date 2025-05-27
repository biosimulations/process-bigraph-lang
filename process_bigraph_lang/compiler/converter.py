from typing import Any

from process_bigraph_lang.compiler.pb_model import PBModel


def assemble_pb(pb_model: PBModel) -> dict[str, Any]:
    doc: dict[str, Any] = dict(composition={}, state={})
    for store in pb_model.stores:
        if store.value is not None:
            set_value_at_path(doc["state"], store.full_path, value=store.value)
        if store.data_type:
            set_value_at_path(doc["composition"], store.full_path, value=store.data_type)
    for step in pb_model.steps:
        address = step.address
        if not address.startswith("local:"):
            address = "local:!" + address
        address_dict = dict(_type="quote", _default=address)
        step_schema_dict: dict[str, Any] = dict(_type=step._type, address=address_dict)
        if step.config_schema:
            step_schema_dict["_config"] = step.config_schema
        if step.input_schema:
            step_schema_dict["_inputs"] = step.input_schema
        if step.output_schema:
            step_schema_dict["_outputs"] = step.output_schema
        set_value_at_path(doc["composition"], step.full_path, value=step_schema_dict)

        step_state_dict: dict[str, Any] = dict(_type=step._type)
        if step.config_state:
            step_state_dict["config"] = step.config_state
        if step.input_state:
            step_state_dict["inputs"] = step.input_state
        if step.output_state:
            step_state_dict["outputs"] = step.output_state
        set_value_at_path(doc["state"], step.full_path, value=step_state_dict)

    for process in pb_model.processes:
        address = process.address
        if not address.startswith("local:"):
            address = "local:!" + address
        address_dict = dict(_type="quote", _default=address)
        process_schema_dict: dict[str, Any] = dict(_type=process._type, address=address_dict)
        if process.config_schema:
            process_schema_dict["_config"] = process.config_schema
        if process.input_schema:
            process_schema_dict["_inputs"] = process.input_schema
        if process.output_schema:
            process_schema_dict["_outputs"] = process.output_schema
        set_value_at_path(doc["composition"], process.full_path, value=process_schema_dict)

        address = process.address
        if not address.startswith("local:"):
            address = "local:!" + address
        process_state_dict: dict[str, Any] = dict(_type=process._type)
        if process.config_state:
            process_state_dict["config"] = process.config_state
        if process.input_state:
            process_state_dict["inputs"] = process.input_state
        if process.output_state:
            process_state_dict["outputs"] = process.output_state
        if process.interval is not None:
            process_state_dict["interval"] = process.interval
        set_value_at_path(doc["state"], process.full_path, value=process_state_dict)

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
