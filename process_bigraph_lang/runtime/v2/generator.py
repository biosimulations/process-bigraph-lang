from typing import Any

from process_bigraph_lang.runtime.v2.pb_model import PBModel


def generate(pb_model: PBModel) -> dict[str, Any]:
    doc: dict[str, Any] = dict(composition={}, state={})
    for store in pb_model.stores:
        if store.value is not None:
            set_value_at_path(doc["state"], store.full_path, value=store.value)
        if store.data_type:
            set_value_at_path(doc["composition"], store.full_path, value=store.data_type)
    for step in pb_model.steps:
        step_dict: dict[str, Any] = dict(_type=step._type, address=step.address)
        if step.config:
            step_dict["config"] = step.config
        if step.inputs:
            step_dict["inputs"] = step.inputs
        if step.outputs:
            step_dict["outputs"] = step.outputs
        set_value_at_path(doc["state"], step.full_path, value=step_dict)
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
