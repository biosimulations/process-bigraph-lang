"""
The v2 model -> documents.

`write_document` produces the process-bigraph 1.x `{"schema", "state"}` document (plus composite options
at the top level); `write_composite_spec` produces a CompositeSpec mapping ready for `yaml.safe_dump`.
Both are the exact inverse of the reader for every form it accepts.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from process_bigraph_lang.v2.model import (
    MODEL_BLOCKS,
    Address,
    Composite,
    Document,
    Edge,
    ExternalRef,
    ModelDecl,
    ModelRef,
    Node,
    Param,
    ParamRef,
    Site,
    Store,
)
from process_bigraph_lang.v2.paths import wire_to_document
from process_bigraph_lang.v2.types import Named, to_bigraph
from process_bigraph_lang.v2.values import MISSING

AssetLoader = Callable[[ExternalRef], Any]


def write_document(doc: Document, *, assets: AssetLoader | None = None) -> dict[str, Any]:
    """The `{"schema", "state", **options}` document. `assets` loads values the printer externalized."""
    models = {m.name: m for m in doc.models}
    schema, state = _composite(doc.root, assets, models)
    out: dict[str, Any] = {"schema": schema, "state": state}
    out.update(doc.options)
    return out


def write_composite_spec(doc: Document, *, assets: AssetLoader | None = None) -> dict[str, Any]:
    """A CompositeSpec mapping: `name`, `description`, `tags`, `requires`, `parameters`, `emitters`, `schema`, `state`."""
    out: dict[str, Any] = {}
    if doc.name:
        out["name"] = doc.name
    if doc.description:
        out["description"] = doc.description
    if doc.tags:
        out["tags"] = list(doc.tags)
    if doc.requires:
        out["requires"] = dict(doc.requires)
    if doc.params:
        out["parameters"] = {p.name: _param(p) for p in doc.params}
    if doc.emitters:
        out["emitters"] = [
            {
                "address": str(e.address),
                "paths": [p.to_slash() for p in e.paths],
                **({"config": _value(e.config, assets)} if e.config else {}),
            }
            for e in doc.emitters
        ]
    document = write_document(doc, assets=assets)
    if document["schema"]:
        out["schema"] = document["schema"]
    out["state"] = document["state"]
    for key, value in doc.options.items():
        out[key] = value
    out.update(doc.extras)
    return out


def _param(param: Param) -> dict[str, Any]:
    decl: dict[str, Any] = {}
    if param.type is not None:
        decl["type"] = to_bigraph(param.type)
    if param.default is not MISSING:
        decl["default"] = param.default
    if param.description:
        decl["description"] = param.description
    if param.choices is not None:
        decl["choices"] = list(param.choices)
    return decl


def _composite(
    composite: Composite, assets: AssetLoader | None, models: dict[str, ModelDecl] | None = None
) -> tuple[dict[str, Any], dict[str, Any]]:
    schema: dict[str, Any] = {}
    state: dict[str, Any] = {}
    models = models or {}
    for key, element in composite.children.items():
        if isinstance(element, Store):
            if element.site is not None:
                state[key] = _site(element.site, assets, models)  # an open store has no schema entry (#213)
                continue
            if isinstance(element.value, ModelRef) and element.value.name in models:
                schema[key], state[key] = _model_tree(models[element.value.name])
                continue
            if element.type is not None:
                schema[key] = to_bigraph(element.type)
            if element.value is not MISSING:
                state[key] = _value(element.value, assets)
        elif isinstance(element, Node):
            child_schema, child_state = _composite(Composite(element.children), assets, models)
            if element.type is not None:
                schema[key] = to_bigraph(element.type)
            elif child_schema:
                schema[key] = child_schema
            state[key] = child_state
        else:
            state[key] = _edge(element, assets, models)
    schema.update(composite.schema_extras)
    return schema, state


def _model_tree(decl: ModelDecl) -> tuple[dict[str, Any], dict[str, Any]]:
    """A model header as a subtree: one block per member kind, typed with units, valued with the model's values."""
    schema: dict[str, Any] = {}
    state: dict[str, Any] = {}
    for block in MODEL_BLOCKS:
        fields = decl.block(block)
        if not fields:
            continue
        schema[block] = {k: to_bigraph(f.type) if f.type is not None else "float" for k, f in fields.items()}
        state[block] = {k: f.default for k, f in fields.items() if f.default is not MISSING}
    return schema, state


def _sort_schema(sort: ModelDecl) -> dict[str, Any]:
    """The schema a model sort admits: named members as a struct, `_` or an open block as a map."""
    schema: dict[str, Any] = {}
    for block in MODEL_BLOCKS:
        fields = sort.block(block)
        if not fields and block not in sort.open_blocks:
            continue
        wildcard = fields.get("_")
        if wildcard is not None or block in sort.open_blocks:
            element = to_bigraph(wildcard.type) if wildcard is not None and wildcard.type is not None else "float"
            schema[block] = {"_type": "map", "_value": element}
        else:
            schema[block] = {k: to_bigraph(f.type) if f.type is not None else "float" for k, f in fields.items()}
    return schema


def _edge(edge: Edge, assets: AssetLoader | None, models: dict[str, ModelDecl] | None = None) -> dict[str, Any]:
    node: dict[str, Any] = {"_type": edge.kind}
    if edge.ports is not None:
        if edge.ports.inputs is not None:
            node["_inputs"] = {k: to_bigraph(v) for k, v in edge.ports.inputs.items()}
        if edge.ports.outputs is not None:
            node["_outputs"] = {k: to_bigraph(v) for k, v in edge.ports.outputs.items()}
    if edge.address is not None:
        node["address"] = _address(edge.address, assets)
    config: dict[str, Any] = {}
    if edge.inner is not None:
        inner_schema, inner_state = _composite(edge.inner, assets, models)
        config["state"] = inner_state
        if inner_schema:
            config["schema"] = inner_schema
    if edge.bridge is not None:
        config["bridge"] = edge.bridge
    if edge.interface is not None:
        config["interface"] = edge.interface
    config.update(edge.config)
    if config:
        node["config"] = _value(config, assets)
    if edge.inputs:
        node["inputs"] = {k: wire_to_document(w) for k, w in edge.inputs.items()}
    if edge.outputs:
        node["outputs"] = {k: wire_to_document(w) for k, w in edge.outputs.items()}
    if edge.interval is not None:
        node["interval"] = _value(edge.interval, assets)
    if edge.priority is not None:
        node["priority"] = edge.priority
    for key, value in edge.extras.items():
        node[key] = _value(value, assets)
    return node


def _address(address: Address | Site | ParamRef, assets: AssetLoader | None) -> Any:
    if isinstance(address, Site):
        return _site(address, assets)
    if isinstance(address, ParamRef):
        return _value(address, assets)
    return str(address)


def _site(site: Site, assets: AssetLoader | None, models: dict[str, ModelDecl] | None = None) -> dict[str, Any]:
    sort: Any = to_bigraph(site.sort)
    if isinstance(site.sort, Named) and models and site.sort.name in models and models[site.sort.name].is_sort:
        sort = _sort_schema(models[site.sort.name])
    node: dict[str, Any] = {"_type": "site", "_sort": sort}
    if site.default is not MISSING:
        node["_default"] = _value(site.default, assets)
    return node


def _value(value: Any, assets: AssetLoader | None) -> Any:
    if isinstance(value, ParamRef):
        return value.template if value.template is not None else "${" + value.name + "}"
    if isinstance(value, ExternalRef):
        if assets is None:
            raise ValueError(f"value kept in sidecar '{value.path}' but no asset loader was given")
        return assets(value)
    if isinstance(value, Site):
        return _site(value, assets)
    if isinstance(value, dict):
        return {k: _value(v, assets) for k, v in value.items()}
    if isinstance(value, list):
        return [_value(v, assets) for v in value]
    if isinstance(value, tuple):
        return tuple(_value(v, assets) for v in value)
    return value
